from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.transaction import atomic
from extract.models import *
import csv


class Command(BaseCommand):
    args = "filename"
    help = "Import BHC YouTube videos from a CSV file"

    @atomic
    def handle(self, *args, **options):
        if not args:
            raise CommandError("Missing filename.")
        filename = args[0]
        with open(filename, "r") as f:
            reader = csv.reader(f)
            self.stdout.write(next(reader))     # Skip the first row.
            for row in reader:
                title = row[0]
                summary = row[1]
                html = row[2]

                article = Article()
                article.source = "BHCYT"
                article.title = title
                article.summary = summary
                article.content = '<p class="bhc-youtube-summary">' + \
                    summary + '</p>' + html
                article.last_modified = timezone.now()
                article.remarks = "{0} {1}".format(__name__, timezone.now())
                article.save()

        self.stdout.write("Done.")
