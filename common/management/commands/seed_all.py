import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.utils import timezone
from wagtail.models import Page, Site
from utils.seeding import SeedingHelper

# Import Models
from news.models import NewsIndexPage, NewsPage, NewsImage
from faculties.models import Faculty, Department, FacultyAchievement
from sections.models import Leader, StructureSection, SectionMember
from science.models import ScienceIndex, ResearchArea, ResearchDetail
from collaboration.models import CollaborationPage, PartnerOrganization, CollaborationProject
from admission.models import AdmissionYear, AdmissionQuota
from activities.models import ActivityCategory, ActivityPage
from common.models import Vacancy, VacancyApplication
from enlightenment.models import EnlightenmentSection, Club, AchievementSection
from navigation.models import DynamicPage, NavItem, SubNavItem, TopBarLink
from appeals.models import Appeal
from collaboration.models import CollaborationType, PartnerOrganization, CollaborationProject, CollaborationPage
from information_systems.models import InformationSystem
from hemis.models import HemisStatistic

class Command(BaseCommand):
    help = 'Seed all apps with fake data (20+ items each)'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data')

    def handle(self, *args, **options):
        self.helper = SeedingHelper()
        self.stdout.write(self.style.MIGRATE_HEADING("Starting Seeding Process..."))

        if options['clear']:
            self.clear_data()

        # Ensure we have images
        self.helper.get_or_create_academic_images(15)

        # Get Home Page
        try:
            self.home_page = Page.objects.get(id=3)
        except Page.DoesNotExist:
            self.stdout.write(self.style.ERROR("Home page (id=3) not found. Check your Wagtail installation."))
            return

        with transaction.atomic():
            self.seed_faculties()
            self.seed_news()
            self.seed_sections()
            self.seed_science()
            self.seed_collaboration()
            self.seed_admission()
            self.seed_activities()
            self.seed_common()
            self.seed_appeals()
            self.seed_enlightenment()
            self.seed_information_systems()
            self.seed_hemis()
            self.seed_navigation()

        self.stdout.write(self.style.SUCCESS("\n✅ All apps seeded successfully!"))

    def clear_data(self):
        self.stdout.write(self.style.WARNING("Clearing data..."))
        # Delete Pages (Carefully)
        NewsPage.objects.all().delete()
        NewsIndexPage.objects.all().delete()
        ActivityPage.objects.all().delete()
        CollaborationPage.objects.all().delete()
        
        # Delete Models
        Faculty.objects.all().delete()
        Leader.objects.all().delete()
        StructureSection.objects.all().delete()
        InformationSystem.objects.all().delete()
        Vacancy.objects.all().delete()
        VacancyApplication.objects.all().delete()
        Appeal.objects.all().delete()
        HemisStatistic.objects.all().delete()
        ResearchArea.objects.all().delete()
        ResearchDetail.objects.all().delete()
        CollaborationType.objects.all().delete()
        Club.objects.all().delete()
        EnlightenmentSection.objects.all().delete()
        AchievementSection.objects.all().delete()
        NavItem.objects.all().delete()
        TopBarLink.objects.all().delete()

    def seed_news(self):
        self.stdout.write("Seeding News...")
        index = NewsIndexPage.objects.filter(slug='news').first()
        if not index:
            index = NewsIndexPage(
                title="Yangiliklar",
                slug="news",
            )
            self.helper.fill_translated_fields(index, 'title', lambda f: "Yangiliklar" if f == self.helper.fake_uz else ("Новости" if f == self.helper.fake_ru else "News"))
            self.home_page.add_child(instance=index)
            index.save_revision().publish()

        # 2. News Pages
        for i in range(25):
            title = self.helper.get_localized_text('sentence', nb_words=6)
            news = NewsPage(
                title=title['uz'],
                slug=slugify(title['en'])[:50] + f"-{i}",
                post_type=random.choice(['news', 'announcement']),
                published_date=timezone.now(),
                cover_image=self.helper.get_random_image()
            )
            self.helper.fill_translated_fields(news, 'excerpt', lambda f: f.paragraph())
            self.helper.fill_translated_fields(news, 'content', lambda f: f"<p>{f.text(max_nb_chars=1000)}</p>")
            index.add_child(instance=news)
            news.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 25 News pages created"))

    def seed_faculties(self):
        self.stdout.write("Seeding Faculties...")
        for i in range(20):
            name = self.helper.get_localized_text('company')
            faculty = Faculty(
                faculty_code=f"F{i}",
                cover_image=self.helper.get_random_image(),
                dean_image=self.helper.get_random_image(),
                order=i
            )
            self.helper.fill_translated_fields(faculty, 'name', lambda f: f"{f.company()} fakulteti")
            self.helper.fill_translated_fields(faculty, 'short_description', lambda f: f.sentence())
            self.helper.fill_translated_fields(faculty, 'dean_name', lambda f: f.name())
            faculty.save()
            # Add Faculty Achievements
            for _ in range(3):
                achievement = FacultyAchievement(
                    faculty=faculty,
                    year=random.randint(2015, 2024),
                    image=self.helper.get_random_image()
                )
                self.helper.fill_translated_fields(achievement, 'title', lambda f: f.sentence(nb_words=4))
                achievement.save()

            # 3 Departments per faculty
            for j in range(3):
                dept_name = self.helper.get_localized_text('job')
                dept = Department(
                    faculty=faculty,
                    department_code=f"D{i}{j}",
                    head_image=self.helper.get_random_image(),
                    order=j
                )
                self.helper.fill_translated_fields(dept, 'name', lambda f: f"{f.job()} kafedrasi")
                self.helper.fill_translated_fields(dept, 'head_name', lambda f: f.name())
                dept.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 20 Faculties and 60 Departments created"))

    def seed_sections(self):
        self.stdout.write("Seeding Sections (Leadership)...")
        # 1. Leaders
        for i in range(10):
            leader = Leader(
                email=self.helper.fake_en.email(),
                phone=self.helper.fake_en.phone_number(),
                image=self.helper.get_random_image(),
                order=i
            )
            self.helper.fill_translated_fields(leader, 'full_name', lambda f: f.name())
            self.helper.fill_translated_fields(leader, 'position', lambda f: f.job())
            self.helper.fill_translated_fields(leader, 'academic_degree', lambda f: "Professor")
            leader.save()
        # 2. Structure
        for i in range(5):
            section = StructureSection(
                slug=f"section-{i}",
                order=i
            )
            self.helper.fill_translated_fields(section, 'name', lambda f: f.company())
            section.save()
            for j in range(4):
                member = SectionMember(
                    section=section,
                    order=j
                )
                self.helper.fill_translated_fields(member, 'full_name', lambda f: f.name())
                self.helper.fill_translated_fields(member, 'position', lambda f: f.job())
                member.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 10 Leaders and 5 Sections created"))

    def seed_science(self):
        self.stdout.write("Seeding Science...")
        for i in range(20):
            area = ResearchArea()
            self.helper.fill_translated_fields(area, 'title', lambda f: f.sentence(nb_words=4))
            self.helper.fill_translated_fields(area, 'description', lambda f: f.text())
            area.save()
            detail = ResearchDetail(
                area=area,
                main_image=self.helper.get_random_image()
            )
            self.helper.fill_translated_fields(detail, 'content', lambda f: f.paragraph())
            detail.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 20 Research areas created"))

    def seed_collaboration(self):
        self.stdout.write("Seeding Collaboration...")
        from collaboration.models import CollaborationType
        for k in range(3):
            ctype = CollaborationType(
                order=k
            )
            self.helper.fill_translated_fields(ctype, 'title', lambda f: f.word().capitalize())
            ctype.save()
            for i in range(7):
                partner = PartnerOrganization(
                    collaboration_type=ctype,
                    website=self.helper.fake_en.url(),
                    logo=self.helper.get_random_image(),
                    order=i
                )
                self.helper.fill_translated_fields(partner, 'name', lambda f: f.company())
                self.helper.fill_translated_fields(partner, 'country', lambda f: "O'zbekiston")
                partner.save()
                # Create some projects for partners
                if i % 2 == 0:
                    project = CollaborationProject(
                        collaboration_type=ctype,
                        cover_image=self.helper.get_random_image(),
                        start_date=timezone.now().date()
                    )
                    self.helper.fill_translated_fields(project, 'title', lambda f: f.sentence())
                    self.helper.fill_translated_fields(project, 'content', lambda f: f.text())
                    project.save()
                    project.partners.add(partner)
        self.stdout.write(self.style.SUCCESS(f"  ✅ 21 Partner organizations and projects created"))

    def seed_admission(self):
        self.stdout.write("Seeding Admission Info...")
        year, _ = AdmissionYear.objects.get_or_create(title=f"{timezone.now().year}/{timezone.now().year+1}", defaults={'is_active': True})
        for i in range(20):
            quota = AdmissionQuota(
                year=year,
                grant_count=random.randint(10, 50),
                contract_count=random.randint(50, 200)
            )
            self.helper.fill_translated_fields(quota, 'direction_name', lambda f: f.company() + " fakulteti")
            self.helper.fill_translated_fields(quota, 'language', lambda f: "O'zbek")
            quota.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 20 Admission quotas created"))

    def seed_activities(self):
        self.stdout.write("Seeding Activities...")
        for i in range(5):
            category = ActivityCategory(
                cover_image=self.helper.get_random_image()
            )
            self.helper.fill_translated_fields(category, 'name', lambda f: f.word().capitalize())
            category.save()
            for j in range(4):
                page = ActivityPage(
                    category=category,
                    cover_image=self.helper.get_random_image()
                )
                self.helper.fill_translated_fields(page, 'title', lambda f: f.sentence())
                self.helper.fill_translated_fields(page, 'content', lambda f: f"<p>{f.text()}</p>")
                page.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 20 Activity pages created"))

    def seed_common(self):
        self.stdout.write("Seeding Vacancies...")
        for i in range(20):
            vacancy = Vacancy(
                employment_type=random.choice(['full_time', 'part_time']),
                category=random.choice(['academic', 'technical', 'admin']),
                salary_min=random.randint(2000000, 5000000),
                salary_max=random.randint(6000000, 15000000),
                is_active=True
            )
            self.helper.fill_translated_fields(vacancy, 'title', lambda f: f.job())
            self.helper.fill_translated_fields(vacancy, 'department', lambda f: "Axborot texnologiyalari")
            self.helper.fill_translated_fields(vacancy, 'description', lambda f: f.text())
            vacancy.save()
            # Add some applications
            for _ in range(3):
                VacancyApplication.objects.create(
                    vacancy=vacancy,
                    full_name=self.helper.fake_uz.name(),
                    phone=self.helper.fake_en.phone_number()[:20],
                    email=self.helper.fake_en.email(),
                    cover_letter=self.helper.fake_en.text()
                )
        self.stdout.write(self.style.SUCCESS(f"  ✅ 20 Vacancies and 60 applications created"))

    def seed_appeals(self):
        self.stdout.write("Seeding Appeals...")
        for i in range(25):
            Appeal.objects.create(
                full_name=self.helper.fake_uz.name(),
                email=self.helper.fake_en.email(),
                department="Computer Science",
                phone=self.helper.fake_en.phone_number()[:20],
                message=self.helper.fake_uz.paragraph(),
                terms_accepted=True,
                is_read=random.choice([True, False])
            )
        self.stdout.write(self.style.SUCCESS(f"  ✅ 25 Appeals created"))

    def seed_enlightenment(self):
        self.stdout.write("Seeding Enlightenment (Clubs/Achievements)...")
        for i in range(10):
            club = Club(
                cover_image=self.helper.get_random_image()
            )
            self.helper.fill_translated_fields(club, 'name', lambda f: f.word().capitalize())
            self.helper.fill_translated_fields(club, 'description', lambda f: f.text())
            self.helper.fill_translated_fields(club, 'content', lambda f: f"<p>{f.text()}</p>")
            club.save()
        # Enlightenment Sections
        for i in range(5):
            section = EnlightenmentSection(
                order=i
            )
            self.helper.fill_translated_fields(section, 'title', lambda f: f.sentence())
            self.helper.fill_translated_fields(section, 'content', lambda f: f.text())
            section.save()
        # Achievement Sections
        for i in range(5):
            section = AchievementSection(
                order=i
            )
            self.helper.fill_translated_fields(section, 'title', lambda f: f.sentence())
            self.helper.fill_translated_fields(section, 'content', lambda f: f.text())
            section.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 10 Clubs and 10 Enlightenment/Achievement sections created"))

    def seed_information_systems(self):
        self.stdout.write("Seeding Information Systems...")
        for i in range(20):
            system = InformationSystem(
                link=self.helper.fake_en.url(),
                icon=self.helper.get_random_image(),
                order=i
            )
            self.helper.fill_translated_fields(system, 'name', lambda f: f.word().capitalize())
            self.helper.fill_translated_fields(system, 'short_description', lambda f: f.sentence())
            system.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ 20 Information systems created"))

    def seed_hemis(self):
        self.stdout.write("Seeding HEMIS Statistics...")
        # HemisStatistic uses a singleton pattern in its save() method
        HemisStatistic.objects.create(
            students_count=random.randint(5000, 10000),
            teachers_count=random.randint(300, 800),
            efficiency=random.randint(40, 70),
            directions_count=random.randint(30, 60)
        )
        self.stdout.write(self.style.SUCCESS(f"  ✅ HEMIS Statistics created"))

    def seed_navigation(self):
        self.stdout.write("Seeding Navigation...")
        for i in range(5):
            item = NavItem(
                order=i
            )
            self.helper.fill_translated_fields(item, 'title', lambda f: f.word().capitalize())
            item.save()
            # Use some KNOWN_PAGES for children
            pages = ['about', 'leadership', 'structure', 'faculties', 'science', 'admission']
            for j in range(3):
                sub = SubNavItem(
                    parent=item,
                    page_id=pages[(i*3 + j) % len(pages)],
                    order=j
                )
                self.helper.fill_translated_fields(sub, 'title', lambda f: f.word().capitalize())
                sub.save()
        for i in range(5):
            link = TopBarLink(
                order=i
            )
            self.helper.fill_translated_fields(link, 'title', lambda f: f.word().capitalize())
            link.save()
        self.stdout.write(self.style.SUCCESS(f"  ✅ Navigation items created"))

