from django.core.management.base import BaseCommand, CommandError
from extract.models import Article
import csv
import hashlib


class Command(BaseCommand):
    args = "<filename>"
    help = "Export data as a CSV file"

    def handle(self, *args, **options):
        try:
            filename = args[0]
        except IndexError:
            raise CommandError("Missing filename argument.")

        qs = Article.objects.all().select_related("articleattr")
        with open(filename, "w", newline="") as csvfile:
            csvwriter = csv.writer(csvfile)
            # Write header.
            csvwriter.writerow(["id", "title", "length", "media", "similarity",
                                "is_local"])

            # Write content.
            id_set = set()
            for a in qs:
                s = a.title.encode("utf-8")
                article_id = hashlib.sha256(s).hexdigest()[0:8]
                assert article_id not in id_set
                id_set.add(article_id)
                attr = a.articleattr
                csvwriter.writerow([article_id, a.title, attr.length,
                                    attr.media, attr.similarity,
                                    int(attr.is_local)])
