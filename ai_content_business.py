        high_value_avg_price = sum(self.calculate_price(ct, {}) for ct in high_value) / len(high_value)
        high_value_earnings = high_value_orders * high_value_avg_price * 0.85
        
        scenarios['high_value'] = {
            'strategy': 'Low volume, high value content',
            'content_types': high_value,
            'monthly_orders': round(high_value_orders),
            'avg_price': round(high_value_avg_price, 2),
            'monthly_earnings': round(high_value_earnings, 2),
            'hourly_rate': round(high_value_earnings / total_hours, 2)
        }
        
        # Scenario 3: Mixed approach (balanced)
        mixed = ['blog_post', 'seo_article', 'social_media']
        mixed_hours = sum(time_estimates[ct] for ct in mixed) / len(mixed)
        mixed_orders = total_hours / mixed_hours
        mixed_avg_price = sum(self.calculate_price(ct, {}) for ct in mixed) / len(mixed)
        mixed_earnings = mixed_orders * mixed_avg_price * 0.85
        
        scenarios['mixed'] = {
            'strategy': 'Balanced mix of content types',
            'content_types': mixed,
            'monthly_orders': round(mixed_orders),
            'avg_price': round(mixed_avg_price, 2),
            'monthly_earnings': round(mixed_earnings, 2),
            'hourly_rate': round(mixed_earnings / total_hours, 2)
        }
        
        # Save scenarios
        with open('earnings_scenarios.json', 'w') as f:
            json.dump(scenarios, f, indent=2)
        
        return scenarios
    
    def generate_business_report(self):
        """Generate business performance report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'clients': len(self.clients),
            'active_clients': len([c for c in self.clients if c['status'] == 'active']),
            'total_orders': len(self.orders),
            'pending_orders': len([o for o in self.orders if o['status'] == 'pending']),
            'completed_orders': len([o for o in self.orders if o['status'] == 'completed']),
            'total_earnings': round(self.earnings, 2),
            'total_expenses': round(self.expenses, 2),
            'net_profit': round(self.earnings - self.expenses, 2),
            'top_clients': sorted(self.clients, key=lambda x: x['total_spent'], reverse=True)[:5],
            'popular_content': {},
            'platform_breakdown': {}
        }
        
        # Popular content types
        content_counts = {}
        for order in self.orders:
            ct = order['content_type']
            content_counts[ct] = content_counts.get(ct, 0) + 1
        
        report['popular_content'] = sorted(
            [{'type': ct, 'count': count, 'name': self.content_types[ct]['name']} 
             for ct, count in content_counts.items()],
            key=lambda x: x['count'],
            reverse=True
        )[:5]
        
        # Platform breakdown
        platform_counts = {}
        platform_earnings = {}
        for order in self.orders:
            platform = order.get('platform', 'direct')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            if order['status'] == 'completed':
                platform_earnings[platform] = platform_earnings.get(platform, 0.0) + order['price']
        
        report['platform_breakdown'] = {
            'counts': platform_counts,
            'earnings': platform_earnings
        }
        
        # Save report
        with open('business_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info("✅ Business report generated")
        return report
    
    def generate_marketing_materials(self):
        """Generate marketing materials for freelance platforms"""
        materials = {
            'upwork_profile': {
                'title': 'AI-Powered Content Creator | SEO Articles, Blog Posts, Social Media',
                'overview': """I'm a professional content creator leveraging cutting-edge AI technology to deliver high-quality, engaging content at scale. With AI assistance, I can produce SEO-optimized articles, compelling blog posts, and engaging social media content faster and more efficiently than traditional methods.

My AI-enhanced workflow allows me to:
• Research and outline topics in minutes
• Generate well-structured drafts with proper SEO elements
• Edit and polish for human-like quality and tone
• Deliver consistent, high-quality content on tight deadlines

I specialize in:
✅ SEO Articles & Blog Posts (500-2000 words)
✅ Social Media Content & Strategy
✅ Product Descriptions & E-commerce Copy
✅ Email Newsletters & Marketing Copy
✅ Landing Pages & Sales Funnels

Why choose AI-powered content?
• 50-70% faster delivery times
• Consistent quality and tone
• SEO optimization built-in
• Scalable for large projects
• Cost-effective for businesses

Let's discuss how AI-powered content can transform your marketing strategy!""",
                'hourly_rate': '$25-50/hour',
                'portfolio_link': 'portfolio_samples.json'
            },
            'fiverr_gig': {
                'title': 'I will write AI-powered SEO articles, blog posts, and social media content',
                'description': """🚀 GET HIGH-QUALITY AI-POWERED CONTENT FAST! 🚀

Need engaging, SEO-optimized content but short on time? I use advanced AI technology combined with human editing to deliver professional content at lightning speed!

✨ WHAT YOU GET:
• 100% original, plagiarism-free content
• SEO optimization with keywords
• Proper formatting with headings
• Engaging tone tailored to your audience
• Fast delivery (1-3 days)

📝 SERVICES:
✅ SEO Articles (500-2000 words)
✅ Blog Posts on any topic
✅ Social Media Posts (Instagram, Twitter, LinkedIn)
✅ Product Descriptions
✅ Email Newsletters
✅ Website Copy

🤖 WHY AI-POWERED?
• Faster delivery (save 50-70% time)
• Consistent quality
• Cost-effective
• Scalable for large projects
• Human-edited for perfect results

💼 MY PROCESS:
1. Topic research & keyword analysis
2. AI-assisted draft generation
3. Human editing & polishing
4. SEO optimization
5. Final delivery with revisions

📈 PERFECT FOR:
• Bloggers & content marketers
• E-commerce stores
• Startups & small businesses
• Digital marketing agencies
• Anyone needing quality content fast!

Order now and get your first piece with 20% OFF for new clients!""",
                'packages': [
                    {'name': 'Basic', 'price': '$50', 'delivery': '3 days', 'features': ['500-word article', '1 revision', 'SEO optimization']},
                    {'name': 'Standard', 'price': '$100', 'delivery': '2 days', 'features': ['1000-word article', '2 revisions', 'SEO + images']},
                    {'name': 'Premium', 'price': '$200', 'delivery': '1 day', 'features': ['2000-word article', '3 revisions', 'Full package']}
                ]
            },
            'contentfly_profile': {
                'title': 'AI-Enhanced Content Writer',
                'bio': 'Professional writer using AI tools to deliver high-quality, SEO-optimized content faster and more efficiently. Specializing in blog posts, articles, and marketing copy.',
                'specialties': ['SEO Writing', 'Blog Posts', 'Marketing Copy', 'Social Media', 'E-commerce'],
                'rate': '$0.08-0.12 per word'
            }
        }
        
        # Save marketing materials
        with open('marketing_materials.json', 'w') as f:
            json.dump(materials, f, indent=2)
        
        logger.info("✅ Marketing materials generated")
        return materials

def main():
    """Main function - AI Content Business System"""
    business = AIContentBusiness()
    
    print("="*80)
    print("🤖 AI CONTENT CREATION BUSINESS SYSTEM")
    print("="*80)
    print("💰 Complete business-in-a-box for making money with AI content")
    print("="*80)
    
    while True:
        print("\n" + "="*80)
        print("📋 MAIN MENU")
        print("="*80)
        print("1. 📝 Create New Order")
        print("2. 📊 View Business Report")
        print("3. 🎨 Generate Portfolio Samples")
        print("4. 💰 Calculate Earnings Potential")
        print("5. 📢 Generate Marketing Materials")
        print("6. 👥 View Clients")
        print("7. 📦 View Orders")
        print("8. ✅ Complete Order")
        print("9. 💾 Save Data")
        print("0. 🚪 Exit")
        print("="*80)
        
        choice = input("\nSelect option (0-9): ").strip()
        
        if choice == '1':
            print("\n" + "="*80)
            print("📝 CREATE NEW ORDER")
            print("="*80)
            
            # Show content types
            print("\nAvailable Content Types:")
            for i, (ct_key, ct_info) in enumerate(business.content_types.items(), 1):
                print(f"{i}. {ct_info['name']} - {ct_info['description']}")
            
            ct_choice = input("\nSelect content type (number or name): ").strip()
            
            # Find content type
            content_type = None
            if ct_choice.isdigit():
                idx = int(ct_choice) - 1
                if 0 <= idx < len(business.content_types):
                    content_type = list(business.content_types.keys())[idx]
            else:
                # Try to find by name
                for ct_key, ct_info in business.content_types.items():
                    if ct_choice.lower() in ct_info['name'].lower():
                        content_type = ct_key
                        break
            
            if not content_type:
                print("❌ Invalid content type selection")
                continue
            
            # Get details
            client_name = input("Client name: ").strip()
            topic = input("Topic (optional): ").strip() or None
            
            details = {'topic': topic} if topic else {}
            
            # Additional details based on content type
            ct_info = business.content_types[content_type]
            
            if content_type in ['blog_post', 'seo_article', 'ebook_chapter']:
                words = input(f"Word count ({ct_info['min_words']}-{ct_info['max_words']}): ").strip()
                if words:
                    details['words'] = int(words)
            
            elif content_type == 'social_media':
                posts = input(f"Number of posts (default {ct_info['posts_per_package']}): ").strip()
                if posts:
                    details['posts'] = int(posts)
            
            elif content_type == 'product_description':
                descs = input(f"Number of descriptions (min {ct_info['min_descriptions']}): ").strip()
                if descs:
                    details['descriptions'] = int(descs)
            
            elif content_type == 'video_script':
                minutes = input(f"Video length in minutes ({ct_info['min_minutes']}-{ct_info['max_minutes']}): ").strip()
                if minutes:
                    details['minutes'] = int(minutes)
            
            # Platform
            print("\nAvailable Platforms:")
            for i, (p_key, p_info) in enumerate(business.platforms.items(), 1):
                print(f"{i}. {p_info['name']} ({p_info['commission']*100}% commission)")
            
            platform_choice = input("\nSelect platform (number or name, or 'direct'): ").strip().lower()
            
            if platform_choice.isdigit():
                idx = int(platform_choice) - 1
                if 0 <= idx < len(business.platforms):
                    details['platform'] = list(business.platforms.keys())[idx]
            elif platform_choice in business.platforms:
                details['platform'] = platform_choice
            elif platform_choice == 'direct':
                details['platform'] = 'direct'
            else:
                details['platform'] = 'direct'
            
            # Rush order?
            rush = input("Rush order? (y/n): ").strip().lower()
            if rush == 'y':
                details['rush'] = True
            
            # Revisions
            revisions = input("Number of revisions included (default 2): ").strip()
            if revisions and revisions.isdigit():
                details['revisions'] = int(revisions)
            
            # Notes
            notes = input("Additional notes (optional): ").strip()
            if notes:
                details['notes'] = notes
            
            # Create order
            order = business.create_order(client_name, content_type, details)
            
            print("\n" + "="*80)
            print("✅ ORDER CREATED SUCCESSFULLY!")
            print("="*80)
            print(f"Order ID: {order['order_id']}")
            print(f"Client: {order['client_name']}")
            print(f"Content: {order['content_name']}")
            print(f"Price: ${order['price']:.2f}")
            print(f"Delivery: {order['delivery_date'][:10]}")
            print(f"Status: {order['status']}")
            print("="*80)
            
            input("\nPress Enter to continue...")
        
        elif choice == '2':
            print("\n" + "="*80)
            print("📊 BUSINESS REPORT")
            print("="*80)
            
            report = business.generate_business_report()
            
            print(f"📈 Total Earnings: ${report['total_earnings']:.2f}")
            print(f"💰 Net Profit: ${report['net_profit']:.2f}")
            print(f"👥 Clients: {report['clients']} ({report['active_clients']} active)")
            print(f"📦 Orders: {report['total_orders']} ({report['completed_orders']} completed, {report['pending_orders']} pending)")
            
            print("\n🏆 Top Clients:")
            for i, client in enumerate(report['top_clients'][:3], 1):
                print(f"  {i}. {client['name']} - ${client['total_spent']:.2f} ({client['order_count']} orders)")
            
            print("\n🎯 Popular Content Types:")
            for i, content in enumerate(report['popular_content'][:3], 1):
                print(f"  {i}. {content['name']} - {content['count']} orders")
            
            print("\n📱 Platform Breakdown:")
            for platform, count in report['platform_breakdown']['counts'].items():
                earnings = report['platform_breakdown']['earnings'].get(platform, 0)
                print(f"  • {platform}: {count} orders (${earnings:.2f})")
            
            print("\n✅ Report saved to 'business_report.json'")
            input("\nPress Enter to continue...")
        
        elif choice == '3':
            print("\n" + "="*80)
            print("🎨 GENERATING PORTFOLIO SAMPLES")
            print("="*80)
            
            count = input("How many samples? (default 5): ").strip()
            count = int(count) if count.isdigit() else 5
            
            samples = business.generate_portfolio_samples(count)
            
            print(f"\n✅ Generated {len(samples)} portfolio samples:")
            for i, sample in enumerate(samples, 1):
                print(f"\n{i}. {sample['content_name']}")
                print(f"   Title: {sample['title']}")
                print(f"   Price Example: ${sample['price_example']:.2f}")
                print(f"   Delivery: {sample['delivery_time']}")
            
            print("\n✅ Samples saved to 'portfolio_samples.json'")
            input("\nPress Enter to continue...")
        
        elif choice == '4':
            print("\n" + "="*80)
            print("💰 EARNINGS POTENTIAL CALCULATION")
            print("="*80)
            
            hours = input("Hours per day you can work (default 4): ").strip()
            hours = int(hours) if hours.isdigit() else 4
            
            scenarios = business.calculate_monthly_earnings_potential(hours)
            
            print(f"\n📅 Based on {hours} hours/day, 22 working days/month:")
            print("="*80)
            
            for scenario_name, scenario in scenarios.items():
                print(f"\n{scenario_name.upper().replace('_', ' ')}:")
                print(f"  Strategy: {scenario['strategy']}")
                print(f"  Content: {', '.join(scenario['content_types'])}")
                print(f"  Monthly Orders: {scenario['monthly_orders']}")
                print(f"  Avg Price: ${scenario['avg_price']:.2f}")
                print(f"  Monthly Earnings: ${scenario['monthly_earnings']:.2f}")
                print(f"  Hourly Rate: ${scenario['hourly_rate']:.2f}/hour")
            
            print("\n✅ Scenarios saved to 'earnings_scenarios.json'")
            input("\nPress Enter to continue...")
        
        elif choice == '5':
            print("\n" + "="*80)
            print("📢 GENERATING MARKETING MATERIALS")
            print("="*80)
            
            materials = business.generate_marketing_materials()
            
            print("✅ Marketing materials generated for:")
            print(f"  • Upwork: {materials['upwork_profile']['title']}")
            print(f"  • Fiverr: {materials['fiverr_gig']['title']}")
            print(f"  • ContentFly: {materials['contentfly_profile']['title']}")
            
            print("\n📝 Sample Upwork overview (first 200 chars):")
            print(materials['upwork_profile']['overview'][:200] + "...")
            
            print("\n✅ Materials saved to 'marketing_materials.json'")
            input("\nPress Enter to