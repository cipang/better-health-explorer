from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.transaction import atomic
from extract.models import *
from bs4 import BeautifulSoup
import os
import re


class Command(BaseCommand):
    args = "filename"
    help = "Extract information from BHC articles"
    re_link = re.compile(r"\A[a-z]+\://")

    def handle(self, *args, **options):
        for filename in args:
            try:
                basename = os.path.basename(filename)
                result = self.do_file(filename)
                self.stdout.write("{0}: {1} images; {2} links.".format(
                    basename, result[0], result[1]))
            except Exception as e:
                raise CommandError("{0}: {1}".format(basename, e))

    @atomic
    def do_file(self, filename):
        soup = BeautifulSoup(open(filename, "r", encoding="cp1252"))
        article = Article()
        article.source = "BHC"
        article.title = soup.title.text.replace(" - Better Health Channel", "")

        summary = soup.find("p", class_="summary").text
        article.summary = str(summary).replace("\n", "")

        body_children = list(soup.body.children)
        categories = str(body_children[0]).replace("\n", "").split(" > ")
        article.category = "/".join(categories)
        del body_children[0]

        content = (str(x).replace("</br>", "").strip() for x in body_children)
        article.content = "\n".join(filter(None, content))

        article.last_modified = timezone.now()
        article.remarks = "{0} {1}".format(__name__, timezone.now())
        article.save()

        # Handle images.
        img_count = 0
        all_images = soup.body.find_all("img", src=True)
        for img in all_images:
            image = Image(article=article)
            image.src = img["src"]
            image.alt = img["alt"]
            image.save()
            img_count += 1

        # Handle hyperlinks.
        link_count = 0
        all_links = soup.body.find_all("a", href=True)
        for link in all_links:
            ol = OutLink(article=article)
            ol.target_url = link["href"]
            if self.re_link.match(ol.target_url):
                ol.target_source = "WWW"
            else:
                ol.target_source = article.source
            ol.alt = str(link.string)[0:200]
            ol.save()
            link_count += 1

        return (img_count, link_count)
