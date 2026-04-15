import os
import requests
from django.core.files.base import ContentFile
from wagtail.images import get_image_model
from faker import Faker

Image = get_image_model()

# Academic theme keywords for placeholder images
ACADEMIC_KEYWORDS = [
    'university', 'library', 'students', 'professor', 'classroom',
    'laboratory', 'campus', 'books', 'graduation', 'lecture'
]

class SeedingHelper:
    def __init__(self):
        self.fake_uz = Faker('uz_UZ')
        self.fake_ru = Faker('ru_RU')
        self.fake_en = Faker('en_US')
        self.images = []

    def get_or_create_academic_images(self, count=10):
        """Create a pool of academic images if they don't exist."""
        if Image.objects.filter(title__startswith="Seed-").count() >= count:
            self.images = list(Image.objects.filter(title__startswith="Seed-")[:count])
            return self.images

        print(f"Downloading {count} academic images...")
        for i in range(count):
            url = f"https://picsum.photos/seed/{i}/800/600"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    image_name = f"seed_image_{i}.jpg"
                    img = Image(
                        title=f"Seed-Image-{i}",
                        file=ContentFile(response.content, name=image_name)
                    )
                    img.save()
                    self.images.append(img)
            except Exception as e:
                print(f"Failed to download image {i}: {e}")

        return self.images

    def get_random_image(self):
        import random
        if not self.images:
            return None
        return random.choice(self.images)

    def fill_translated_fields(self, obj, field_name, value_generator):
        """Fill _uz, _ru, _en fields IF they exist on the object."""
        for lang, fake in [('uz', self.fake_uz), ('ru', self.fake_ru), ('en', self.fake_en)]:
            attr = f"{field_name}_{lang}"
            if hasattr(obj, attr):
                setattr(obj, attr, value_generator(fake))
            elif lang == 'uz': # Fallback to base field
                if hasattr(obj, field_name):
                    setattr(obj, field_name, value_generator(fake))

    def get_localized_text(self, provider_name, **kwargs):
        """Get random text in 3 languages."""
        return {
            'uz': getattr(self.fake_uz, provider_name)(**kwargs),
            'ru': getattr(self.fake_ru, provider_name)(**kwargs),
            'en': getattr(self.fake_en, provider_name)(**kwargs),
        }
