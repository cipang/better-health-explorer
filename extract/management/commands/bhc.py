from django.core.management.base import BaseCommand
from django.utils import timezone
from extract.models import Article, Image
from bs4 import BeautifulSoup


class Command(BaseCommand):
    args = "filename"
    help = "Extract information from BHC articles"

    def handle(self, *args, **options):
        filename = args[0]
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

        output_msg = "Done: {0}".format(article)
        if img_count:
            output_msg += " (with {0} images)".format(img_count)
        self.stdout.write(output_msg)
