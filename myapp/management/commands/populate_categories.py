from django.core.management.base import BaseCommand
from myapp.models import Category

class Command(BaseCommand):
    help = 'Populate computer parts categories'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Processors (CPU)', 'description': 'Intel, AMD processors and CPU coolers'},
            {'name': 'Graphics Cards (GPU)', 'description': 'NVIDIA, AMD graphics cards'},
            {'name': 'Motherboards', 'description': 'ATX, Micro-ATX, Mini-ITX motherboards'},
            {'name': 'Memory (RAM)', 'description': 'DDR4, DDR5 RAM modules'},
            {'name': 'Storage (SSD/HDD)', 'description': 'Solid State Drives, Hard Disk Drives'},
            {'name': 'Power Supply (PSU)', 'description': 'Modular and non-modular PSUs'},
            {'name': 'Computer Cases', 'description': 'Mid-tower, Full-tower, Mini cases'},
            {'name': 'Cooling Systems', 'description': 'Air coolers, liquid cooling, case fans'},
            {'name': 'Monitors', 'description': 'LCD, LED, Gaming monitors'},
            {'name': 'Keyboards', 'description': 'Mechanical, membrane, gaming keyboards'},
            {'name': 'Mice', 'description': 'Gaming, wireless, wired mice'},
            {'name': 'Headsets & Audio', 'description': 'Gaming headsets, speakers'},
            {'name': 'Networking', 'description': 'Routers, WiFi adapters, network cards'},
            {'name': 'Cables & Adapters', 'description': 'HDMI, DisplayPort, USB cables'},
            {'name': 'Peripherals', 'description': 'Webcams, microphones, accessories'},
        ]
        
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {category.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Already exists: {category.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✓ Total categories: {Category.objects.count()}'))