#!/usr/bin/env python3
"""
TEST AI CONTENT GENERATOR
Test the AI content generation system
"""

from ai_content_generator import AIContentGenerator
import json

def main():
    print("="*80)
    print("🤖 TESTING AI CONTENT GENERATOR")
    print("="*80)
    
    generator = AIContentGenerator()
    
    # Test 1: Generate blog post
    print("\n1. 📝 GENERATING BLOG POST")
    print("-"*40)
    
    blog_post = generator.generate_blog_post(
        topic="AI Content Creation",
        word_count=1000,
        keywords=["AI", "content", "writing", "SEO"]
    )
    
    print(f"Title: {blog_post['title']}")
    print(f"Word Count: {blog_post['word_count']}")
    print(f"SEO Score: {blog_post['seo_score']}/100")
    print(f"Readability: {blog_post['readability_score']}/100")
    print(f"AI Model: {blog_post['ai_model']}")
    
    # Save to file
    with open('sample_blog_post.txt', 'w') as f:
        f.write(blog_post['content'])
    print("✅ Saved to: sample_blog_post.txt")
    
    # Test 2: Generate social media posts
    print("\n2. 📱 GENERATING SOCIAL MEDIA POSTS")
    print("-"*40)
    
    social_posts = generator.generate_social_media_posts(
        topic="Content Marketing",
        platform="instagram",
        count=3
    )
    
    for i, post in enumerate(social_posts, 1):
        print(f"\nPost #{i} ({post['type']}):")
        print(f"Engagement Score: {post['engagement_score']}/100")
        print(f"Content: {post['content'][:100]}...")
    
    # Save to file
    with open('sample_social_posts.json', 'w') as f:
        json.dump(social_posts, f, indent=2)
    print("✅ Saved to: sample_social_posts.json")
    
    # Test 3: Generate product descriptions
    print("\n3. 🛍️ GENERATING PRODUCT DESCRIPTIONS")
    print("-"*40)
    
    product_descriptions = generator.generate_product_descriptions(
        product_name="AI Writing Assistant Pro",
        features=["Fast content generation", "SEO optimization", "Multiple languages", "Plagiarism check"],
        count=2
    )
    
    for i, desc in enumerate(product_descriptions, 1):
        print(f"\nDescription #{i} ({desc['angle']}):")
        print(f"Persuasion Score: {desc['persuasion_score']}/100")
        print(f"Content: {desc['content'][:100]}...")
    
    # Save to file
    with open('sample_product_descriptions.json', 'w') as f:
        json.dump(product_descriptions, f, indent=2)
    print("✅ Saved to: sample_product_descriptions.json")
    
    # Test 4: Generate email newsletter
    print("\n4. 📧 GENERATING EMAIL NEWSLETTER")
    print("-"*40)
    
    newsletter = generator.generate_email_newsletter(
        topic="Digital Marketing",
        audience="subscribers"
    )
    
    print(f"Subject: {newsletter['subject']}")
    print(f"Preheader: {newsletter['preheader']}")
    print(f"Open Rate Prediction: {newsletter['open_rate_prediction']}")
    print(f"Click Rate Prediction: {newsletter['click_rate_prediction']}")
    
    # Save to file
    with open('sample_newsletter.html', 'w') as f:
        f.write(newsletter['content'])
    with open('sample_newsletter.txt', 'w') as f:
        f.write(newsletter['plain_text'])
    print("✅ Saved to: sample_newsletter.html and sample_newsletter.txt")
    
    print("\n" + "="*80)
    print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)
    print("\n📁 SAMPLE FILES CREATED:")
    print("  • sample_blog_post.txt - Sample blog post")
    print("  • sample_social_posts.json - Social media posts")
    print("  • sample_product_descriptions.json - Product descriptions")
    print("  • sample_newsletter.html/.txt - Email newsletter")
    
    print("\n🚀 READY TO START YOUR AI CONTENT BUSINESS!")
    print("="*80)

if __name__ == '__main__':
    main()