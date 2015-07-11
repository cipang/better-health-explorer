# To convert XML from Western 1252 to UTF-8 in Bash:
# for file in *.xml
# do
#   iconv -f cp1252 -t utf8 $file > ../output/$file
# done

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.transaction import atomic
from extract.models import *
from bs4 import BeautifulSoup
from progress.bar import Bar
import xml.etree.ElementTree as ET
import os
import re
import traceback


class Command(BaseCommand):
    args = "filename"
    help = "Extract information from BHC articles"
    re_link = re.compile(r"\A[a-z]+\://")

    def handle(self, *args, **options):
        if len(args) == 0 or not args[0]:
            raise CommandError("No path is provided.")

        path = args[0]
        bar = Bar("Importing...",
                  suffix="%(percent)d%% %(index)d/%(max)d ETA %(eta_td)s")
        for filename in bar.iter(os.listdir(path)):
            basename = os.path.basename(filename)
            filename = os.path.join(path, filename)
            try:
                self.do_file(filename)
            except Exception as e:
                traceback.print_exc()
                raise CommandError("{0}: {1}".format(basename, e))

    @atomic
    def do_file(self, filename):
        tree = ET.parse(open(filename, "r", encoding="utf8"))
        root = tree.getroot()
        xml_content = root.find("Content")
        xml_ia = root.find("IA")
        xml_kwr = root.find("KeywordsRelated")
        xml_cp = root.find("ContentPartner")

        # Process content XML.
        unique_key = xml_content.find("UniqueKey").text
        title = xml_content.find("Title").text
        summary = xml_content.find("Summary").text
        content = xml_content.find("Body").text.strip()
        content_partner = xml_cp.find("Name").text.strip()

        # Categories.
        cat2 = xml_ia.find("Level2").text or ""
        cat3 = [x.text for x in xml_ia.find("Level3").findall("Item")]
        cat35 = [x.text for x in xml_ia.find("Level35").findall("Item")]
        category = "/".join(filter(None, [cat2,
                                          cat3[0] if cat3 else None,
                                          cat35[0] if cat35 else None]))

        # Keywords.
        keywords = [x.text for x in xml_kwr.find("Keywords").findall("Item")]

        # Parse relative links and append to the content.
        related_facts = list()
        soup = BeautifulSoup(xml_content.find("RelatedFactsheets").text)
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            href = link["href"].replace("?open", "")
            if "/" in href:
                href = href[href.rfind("/") + 1:]
            text = str(link.string)
            related_facts.append((href, text))
        if related_facts:
            content += "<h2>Related information</h2><ul>" + \
                       "\n".join(["<li><a href=\"{0}\">{1}</a></li>".format(*x) for x in related_facts]) + \
                       "</ul>"

        # Construct a DB record.
        article = Article()
        article.source = "BHC"
        article.unique_key = unique_key
        article.title = title
        article.summary = summary
        article.content = content
        article.category = category
        article.cat2 = cat2
        article.provider = content_partner

        # body_children = list(soup.body.children)
        # categories = str(body_children[0]).replace("\n", "").split(" > ")
        # article.category = "/".join(categories)
        # del body_children[0]

        # content = (str(x).replace("</br>", "").strip() for x in body_children)
        # article.content = "\n".join(filter(None, content))

        article.last_modified = timezone.now()
        article.remarks = "{0} {1}".format(__name__, timezone.now())
        article.save()

        # Add Keyword, Category3 and Category35 records.
        for s in filter(None, keywords):
            c = Keyword(article=article)
            c.name = s
            c.save()
        for s in filter(None, cat3):
            c = Category3(article=article)
            c.name = s
            c.save()
        for s in filter(None, cat35):
            c = Category35(article=article)
            c.name = s
            c.save()

        # Parse content HTML.
        soup = BeautifulSoup(content)

        # Handle images.
        img_count = 0
        all_images = soup.find_all("img", src=True)
        for img in all_images:
            src = img["src"]
            if src.endswith("ecblank.gif"):
                continue
            src = src.replace("../../", "/bhcv2/")

            image = Image(article=article)
            image.src = src
            image.alt = img.get("alt", "")
            image.save()
            img_count += 1

        # Handle hyperlinks.
        link_count = 0
        all_links = soup.find_all("a", href=True)
        for link in all_links:
            ol = OutLink(article=article)
            ol.target_url = link["href"]
            if self.re_link.match(ol.target_url):
                ol.target_source = "WWW"
            else:
                ol.target_source = article.source
            ol.alt = str(link.string)
            ol.save()
            link_count += 1

        return (img_count, link_count)
