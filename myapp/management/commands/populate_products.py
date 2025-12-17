from django.core.management.base import BaseCommand
from myapp.models import Product, Category, User
from django.core.files.base import ContentFile
from decimal import Decimal
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import urllib.request

class Command(BaseCommand):
    help = 'Generate dummy computer products with images'

    def create_product_image(self, product_name, category_name, color):
        """Create a product image with category-specific styling"""
        # Create base image with gradient
        img = Image.new('RGB', (600, 600), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background
        for i in range(600):
            r = int(color[0] + (255 - color[0]) * (i / 600))
            g = int(color[1] + (255 - color[1]) * (i / 600))
            b = int(color[2] + (255 - color[2]) * (i / 600))
            draw.rectangle([0, i, 600, i+1], fill=(r, g, b))
        
        # Draw border
        draw.rectangle([30, 30, 570, 570], outline='white', width=5)
        
        # Draw category badge
        draw.rectangle([40, 40, 300, 90], fill=(0, 0, 0, 180))
        draw.text((50, 50), category_name[:20], fill='white')
        
        # Draw product name (split into lines if too long)
        words = product_name.split()
        lines = []
        current_line = []
        
        for word in words:
            current_line.append(word)
            if len(' '.join(current_line)) > 20:
                if len(current_line) > 1:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw product name centered
        y_offset = 250
        for line in lines[:3]:  # Max 3 lines
            draw.text((60, y_offset), line, fill='white')
            y_offset += 40
        
        # Draw decorative elements
        draw.ellipse([450, 450, 550, 550], outline='white', width=3)
        draw.rectangle([50, 520, 150, 560], fill='white')
        draw.text((60, 530), 'TECH', fill=color)
        
        # Save to bytes
        img_io = BytesIO()
        img.save(img_io, format='PNG', quality=95)
        img_io.seek(0)
        
        return ContentFile(img_io.read(), name=f'{product_name.replace(" ", "_")[:50]}.png')

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('🚀 Starting product generation...'))
        
        # Get or create vendor
        vendor, created = User.objects.get_or_create(
            username='techparts_store',
            defaults={
                'email': 'store@techparts.com',
                'user_type': 'vendor',
                'phone': '09123456789',
                'address': 'Metro Manila, Philippines'
            }
        )
        if created:
            vendor.set_password('vendor123')
            vendor.save()
            self.stdout.write(self.style.SUCCESS('✓ Created demo vendor (username: techparts_store, password: vendor123)'))

        # Comprehensive product database with realistic data
        products_data = {
            'Processors (CPU)': [
                ('Intel Core i9-14900K', '24-core (8P+16E) flagship processor, 6.0GHz boost clock, unlocked multiplier, 36MB cache', '35999', (52, 152, 219)),
                ('AMD Ryzen 9 7950X', '16-core/32-thread Zen 4 processor, 5.7GHz boost, 80MB cache, AM5 socket', '32999', (52, 152, 219)),
                ('Intel Core i7-14700K', '20-core (8P+12E) gaming processor, 5.6GHz boost, excellent gaming performance', '25999', (52, 152, 219)),
                ('AMD Ryzen 7 7800X3D', '8-core with 3D V-Cache technology, ultimate gaming CPU, 104MB total cache', '28999', (52, 152, 219)),
                ('Intel Core i5-14600K', '14-core (6P+8E) processor, 5.3GHz boost, best value for gaming', '15999', (52, 152, 219)),
                ('AMD Ryzen 5 7600X', '6-core/12-thread processor, 5.3GHz boost, great for 1440p gaming', '13999', (52, 152, 219)),
                ('Intel Core i9-13900KS', 'Special edition, 6.0GHz out of box, 24-core extreme performance', '42999', (52, 152, 219)),
                ('AMD Ryzen 9 7900X', '12-core/24-thread powerhouse, perfect for content creation', '29999', (52, 152, 219)),
            ],
            'Graphics Cards (GPU)': [
                ('NVIDIA RTX 4090', '24GB GDDR6X, 16384 CUDA cores, ultimate 4K gaming at 120+ FPS', '95999', (46, 204, 113)),
                ('AMD RX 7900 XTX', '24GB GDDR6, RDNA 3 architecture, excellent 4K performance', '54999', (46, 204, 113)),
                ('NVIDIA RTX 4080', '16GB GDDR6X, 9728 CUDA cores, high-end 4K gaming experience', '68999', (46, 204, 113)),
                ('AMD RX 7900 XT', '20GB GDDR6, 84 compute units, excellent for 1440p and 4K', '47999', (46, 204, 113)),
                ('NVIDIA RTX 4070 Ti', '12GB GDDR6X, 7680 CUDA cores, premium 1440p gaming', '48999', (46, 204, 113)),
                ('AMD RX 7800 XT', '16GB GDDR6, perfect 1440p gaming card, ray tracing capable', '32999', (46, 204, 113)),
                ('NVIDIA RTX 4070', '12GB GDDR6X, excellent 1440p performance, DLSS 3 support', '35999', (46, 204, 113)),
                ('AMD RX 7700 XT', '12GB GDDR6, solid 1440p gaming at high settings', '28999', (46, 204, 113)),
                ('NVIDIA RTX 4060 Ti', '8GB/16GB GDDR6, 1080p champion, efficient power usage', '24999', (46, 204, 113)),
                ('AMD RX 7600', '8GB GDDR6, budget-friendly 1080p gaming excellence', '17999', (46, 204, 113)),
            ],
            'Motherboards': [
                ('ASUS ROG MAXIMUS Z790 HERO', 'Premium Intel Z790 chipset, WiFi 6E, Thunderbolt 4, DDR5 support', '28999', (155, 89, 182)),
                ('MSI MAG X670E Tomahawk WiFi', 'AMD AM5 socket, PCIe 5.0, WiFi 6E, robust VRM design', '18999', (155, 89, 182)),
                ('Gigabyte Z790 AORUS MASTER', 'High-end Intel board, 20+1+2 phase VRM, premium features', '32999', (155, 89, 182)),
                ('ASRock X670E Taichi', 'Premium AMD board, Thunderbolt 4, excellent connectivity', '24999', (155, 89, 182)),
                ('ASUS TUF Gaming B650-PLUS WiFi', 'Value AMD AM5 board, PCIe 4.0, military-grade components', '12999', (155, 89, 182)),
                ('MSI PRO Z790-P WiFi', 'Budget Intel DDR5 board, solid features for the price', '10999', (155, 89, 182)),
                ('Gigabyte B650 AORUS ELITE AX', 'Mid-range AMD board with WiFi 6E and good VRM', '14999', (155, 89, 182)),
                ('ASUS ROG STRIX B760-F', 'Intel B760 gaming board, RGB lighting, PCIe 5.0 ready', '15999', (155, 89, 182)),
            ],
            'Memory (RAM)': [
                ('Corsair Dominator Platinum RGB 64GB DDR5', '6400MHz CL32 (2x32GB), premium RGB lighting, tight timings', '18999', (241, 196, 15)),
                ('G.Skill Trident Z5 RGB 32GB DDR5', '6000MHz CL30 (2x16GB), excellent for gaming and productivity', '9999', (241, 196, 15)),
                ('Kingston FURY Beast 32GB DDR5', '5600MHz CL36 (2x16GB), reliable performance, AMD EXPO certified', '7999', (241, 196, 15)),
                ('Corsair Vengeance 32GB DDR4', '3600MHz CL18 (2x16GB), best DDR4 value for Intel/AMD', '5999', (241, 196, 15)),
                ('G.Skill Ripjaws V 16GB DDR4', '3200MHz CL16 (2x8GB), budget gaming memory', '2999', (241, 196, 15)),
                ('TeamGroup T-Force Delta RGB 32GB DDR5', '6000MHz (2x16GB), affordable RGB DDR5', '8499', (241, 196, 15)),
                ('Crucial Pro 64GB DDR5', '5600MHz (2x32GB), workstation memory, ECC support', '15999', (241, 196, 15)),
                ('Corsair Vengeance RGB 64GB DDR4', '3600MHz (2x32GB), content creation powerhouse', '11999', (241, 196, 15)),
            ],
            'Storage (SSD/HDD)': [
                ('Samsung 990 PRO 2TB', 'PCIe 4.0 NVMe M.2, 7450MB/s read, 6900MB/s write, TLC NAND', '10999', (230, 126, 34)),
                ('WD Black SN850X 1TB', 'Gaming SSD with heatsink, 7300MB/s, optimized for DirectStorage', '6999', (230, 126, 34)),
                ('Crucial P5 Plus 2TB', 'Affordable Gen4 NVMe, 6600MB/s read, Micron 176-layer TLC', '9499', (230, 126, 34)),
                ('Samsung 980 PRO 1TB', 'PCIe 4.0 flagship, 7000MB/s read, reliable performance', '5999', (230, 126, 34)),
                ('Kingston KC3000 2TB', 'High-speed Gen4 NVMe, 7000MB/s, great value proposition', '8999', (230, 126, 34)),
                ('WD Blue SN570 1TB', 'Budget NVMe SSD, 3500MB/s, perfect for everyday use', '3499', (230, 126, 34)),
                ('Seagate FireCuda 530 2TB', 'Fastest Gen4 SSD, 7300MB/s, 5-year warranty', '11999', (230, 126, 34)),
                ('Samsung 870 EVO 2TB', 'SATA SSD, 560MB/s, reliable storage for secondary drives', '7999', (230, 126, 34)),
            ],
            'Power Supply (PSU)': [
                ('Corsair RM1000x', '1000W 80+ Gold fully modular, Japanese capacitors, 10-year warranty', '9999', (231, 76, 60)),
                ('Seasonic FOCUS GX-850', '850W 80+ Gold, 10-year warranty, ultra-quiet operation', '7999', (231, 76, 60)),
                ('EVGA SuperNOVA 850 G6', '850W 80+ Gold, compact 140mm design, efficient cooling', '7499', (231, 76, 60)),
                ('Thermaltake Toughpower GF3 1000W', '1000W 80+ Gold, RGB fan, PCIe 5.0 ready cables', '9499', (231, 76, 60)),
                ('Cooler Master V850 Gold V2', '850W 80+ Gold, silent operation, fully modular', '6999', (231, 76, 60)),
                ('be quiet! Straight Power 11 750W', '750W 80+ Gold, virtually silent, premium German engineering', '6499', (231, 76, 60)),
                ('MSI MPG A850G', '850W 80+ Gold, PCIe 5.0 ready, 10-year warranty', '7999', (231, 76, 60)),
                ('Corsair SF750', '750W 80+ Platinum, SFX form factor, perfect for small builds', '8999', (231, 76, 60)),
            ],
            'Computer Cases': [
                ('Lian Li O11 Dynamic EVO', 'Mid-tower, excellent airflow, tempered glass, E-ATX support', '7999', (149, 165, 166)),
                ('NZXT H7 Flow', 'Mid-tower with mesh front panel, cable management bar', '5999', (149, 165, 166)),
                ('Corsair 5000D Airflow', 'Full-tower, spacious interior, excellent cooling potential', '8999', (149, 165, 166)),
                ('Fractal Design Meshify 2', 'Mid-tower, minimalist Scandinavian design, great airflow', '6499', (149, 165, 166)),
                ('Phanteks Eclipse P500A', 'Mid-tower, RGB lighting, mesh front, dual tempered glass', '6999', (149, 165, 166)),
                ('be quiet! Pure Base 500DX', 'Mid-tower, silent operation, sound-dampening panels', '5499', (149, 165, 166)),
                ('Cooler Master MasterBox H500', 'Mid-tower, dual 200mm RGB fans included', '5999', (149, 165, 166)),
                ('Lian Li Lancool 216', 'Budget mid-tower, great value, excellent thermals', '4999', (149, 165, 166)),
            ],
            'Monitors': [
                ('LG 27GP950-B', '27" 4K 144Hz Nano IPS, HDMI 2.1, perfect for PS5/Xbox', '35999', (26, 188, 156)),
                ('Samsung Odyssey G7', '32" 1440p 240Hz VA curved, 1000R curvature, HDR600', '28999', (26, 188, 156)),
                ('ASUS ROG Swift PG279QM', '27" 1440p 240Hz Fast IPS, G-Sync, extreme gaming', '32999', (26, 188, 156)),
                ('Dell S2721DGF', '27" 1440p 165Hz IPS, excellent value, FreeSync/G-Sync', '18999', (26, 188, 156)),
                ('Acer Nitro XV272U', '27" 1440p 170Hz IPS, budget-friendly gaming monitor', '15999', (26, 188, 156)),
                ('BenQ MOBIUZ EX2710S', '27" 1080p 165Hz IPS, HDRi technology, built-in speakers', '12999', (26, 188, 156)),
                ('Gigabyte M27Q', '27" 1440p 170Hz IPS, KVM switch, USB-C connectivity', '16999', (26, 188, 156)),
                ('AOC 24G2', '24" 1080p 144Hz IPS, budget esports monitor, great colors', '8999', (26, 188, 156)),
            ],
            'Keyboards': [
                ('Ducky One 3 SF', '65% mechanical keyboard, Cherry MX switches, premium PBT keycaps', '7999', (243, 156, 18)),
                ('Keychron K8 Pro', 'TKL wireless mechanical, hot-swappable switches, Mac compatible', '6999', (243, 156, 18)),
                ('Corsair K70 RGB Pro', 'Full-size gaming keyboard, Cherry MX, durable PBT keycaps', '8999', (243, 156, 18)),
                ('Logitech G Pro X', 'TKL tournament keyboard, swappable switches, LIGHTSYNC RGB', '7499', (243, 156, 18)),
                ('Razer BlackWidow V3', 'Full-size mechanical, Razer Green clicky switches', '6999', (243, 156, 18)),
                ('HyperX Alloy Origins Core', 'TKL compact design, HyperX Red linear switches', '4999', (243, 156, 18)),
                ('SteelSeries Apex Pro', 'Adjustable actuation switches, OLED smart display', '11999', (243, 156, 18)),
                ('Royal Kludge RK84', 'Budget 75% hot-swappable, RGB, great value', '2999', (243, 156, 18)),
            ],
            'Mice': [
                ('Logitech G Pro X Superlight', 'Wireless gaming mouse, 63g ultra-light, HERO 25K sensor', '7999', (211, 84, 0)),
                ('Razer Viper V2 Pro', 'Wireless esports mouse, 58g weight, Focus Pro 30K sensor', '7499', (211, 84, 0)),
                ('Logitech G502 X Plus', 'Wireless gaming mouse, adjustable weight, LIGHTFORCE switches', '7999', (211, 84, 0)),
                ('SteelSeries Aerox 3', 'Ultra-light wired mouse, 59g, TrueMove Core sensor', '2999', (211, 84, 0)),
                ('Razer DeathAdder V3', 'Ergonomic design, Focus Pro 30K sensor, 59g', '3999', (211, 84, 0)),
                ('Corsair Dark Core RGB Pro', 'Wireless gaming mouse, Qi charging, 18K DPI', '4999', (211, 84, 0)),
                ('Glorious Model O', 'Honeycomb lightweight design, 67g, RGB lighting', '2499', (211, 84, 0)),
                ('Pulsar X2 Wireless', 'Premium wireless mouse, 59g, PAW3370 sensor', '5999', (211, 84, 0)),
            ],
        }

        total_created = 0
        total_skipped = 0
        
        for category_name, products in products_data.items():
            self.stdout.write(self.style.WARNING(f'\n📦 Processing {category_name}...'))
            
            try:
                # Find category
                category = Category.objects.filter(
                    name__icontains=category_name.split('(')[0].strip()
                ).first()
                
                if not category:
                    self.stdout.write(self.style.ERROR(f'✗ Category not found: {category_name}'))
                    continue
                
                for name, desc, price, color in products:
                    # Check if product already exists
                    if Product.objects.filter(name=name).exists():
                        self.stdout.write(self.style.WARNING(f'  ⊘ Skipped (exists): {name}'))
                        total_skipped += 1
                        continue
                    
                    try:
                        # Create product image
                        image = self.create_product_image(name, category_name, color)
                        
                        # Create product
                        product = Product.objects.create(
                            vendor=vendor,
                            category=category,
                            name=name,
                            description=desc,
                            price=Decimal(price),
                            stock=random.randint(15, 75),
                            image=image,
                            is_active=True,
                        )
                        
                        total_created += 1
                        self.stdout.write(self.style.SUCCESS(f'  ✓ Created: {name} - ₱{price:,}'))
                        
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'  ✗ Failed: {name} - {str(e)}'))
                        continue
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Category error: {str(e)}'))
                continue
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS(f'🎉 Product generation complete!'))
        self.stdout.write(self.style.SUCCESS(f'✓ Created: {total_created} new products'))
        self.stdout.write(self.style.WARNING(f'⊘ Skipped: {total_skipped} existing products'))
        self.stdout.write(self.style.SUCCESS(f'📦 Total in database: {Product.objects.count()} products'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}\n'))