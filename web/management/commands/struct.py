from django.core.management.base import BaseCommand, CommandError
from extract.models import *
from web.models import *
from progress.bar import Bar
import re


class Command(BaseCommand):
    args = ""
    help = "Analyze and store document structure."

    def handle(self, *args, **options):
        re_summary = re.compile(r"<(\w*) class=\"?summary\"?>.*?</\1>",
                                flags=re.I | re.S)
        re_section = re.compile(r"\<h2>(.*?)(</h2>|<br>)", flags=re.I | re.S)
        bar = Bar(width=20,
                  suffix="%(percent)d%% %(index)d/%(max)d %(elapsed_td)s ETA %(eta_td)s")

        qs = Article.objects.filter(source="BHC")
        for a in bar.iter(qs):
            a.section_set.all().delete()
            s = a.content
            n = len(s)
            summary_match = re_summary.search(s)
            start = summary_match.end() + 1 if summary_match else 0
            section_no = 0
            section_name = "Introduction"

            def add_section(content):
                section = Section(section_no=section_no, title=section_name)
                section.article = a
                section.content = content.strip()
                section.save()

            for h2 in re_section.finditer(s):
                if h2.start() >= start:
                    add_section(s[start:h2.start() - 1])
                    section_no += 1
                section_name = h2.group(1)
                start = h2.end()
            else:
                if start < n:
                    add_section(s[start:n])
