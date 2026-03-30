#!/usr/bin/env python3
"""
Stripe Payment Link Generator for $100 Trading Experiment
This creates a test payment link for demonstration.
For production, real Stripe API keys would be used.
"""

import json
import os
from datetime import datetime

def generate_payment_link():
    """Generate a simulated Stripe payment link"""
    
    # Load config
    with open('payment_config.json', 'r') as f:
        config = json.load(f)
    
    # Create payment details
    payment_id = f"pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    amount = config['initial_capital_usd']
    email = config['user_email']
    
    # Simulated Stripe payment link (in reality, this would use Stripe API)
    # For demo purposes, we'll create a local payment processor simulation
    payment_link = f"http://127.0.0.1:5080/pay/{payment_id}"
    
    # Create payment page HTML
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>OpenClaw Trading - $100 Investment</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }}
        .container {{ border: 1px solid #e0e0e0; border-radius: 10px; padding: 30px; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .amount {{ font-size: 48px; font-weight: bold; color: #00d09c; margin: 20px 0; }}
        .info {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .button {{ background: #635bff; color: white; padding: 15px 30px; border: none; border-radius: 5px; 
                  font-size: 18px; cursor: pointer; width: 100%; margin-top: 20px; }}
        .button:hover {{ background: #4a42e6; }}
        .steps {{ margin: 30px 0; }}
        .step {{ margin: 15px 0; padding-left: 20px; position: relative; }}
        .step:before {{ content: "✓"; position: absolute; left: 0; color: #00d09c; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 OpenClaw Trading Experiment</h1>
            <p>AI-Powered $100 Growth Challenge</p>
        </div>
        
        <div style="text-align: center;">
            <div class="amount">${amount}</div>
            <p>Initial Investment</p>
        </div>
        
        <div class="info">
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Payment ID:</strong> {payment_id}</p>
            <p><strong>Fees:</strong> ~$4.20 (96% goes to trading)</p>
        </div>
        
        <div class="steps">
            <h3>What happens after payment:</h3>
            <div class="step">Payment processed via Stripe</div>
            <div class="step">Converted to USDC (stablecoin)</div>
            <div class="step">Transferred to trading wallet</div>
            <div class="step">AI trading begins automatically</div>
            <div class="step">First update within 1 hour</div>
        </div>
        
        <button class="button" onclick="processPayment()">Pay ${amount} with Stripe</button>
        
        <div style="margin-top: 30px; font-size: 12px; color: #666; text-align: center;">
            <p>By proceeding, you agree to this experimental trading demonstration.<br>
            All trades are logged and visible on the dashboard.</p>
        </div>
    </div>
    
    <script>
    function processPayment() {{
        // In reality, this would redirect to Stripe Checkout
        // For demo, we'll simulate successful payment
        alert("Payment simulation: $100 payment processed successfully!\\n\\n" +
              "Next: Converting to crypto and starting trades...\\n" +
              "Check dashboard for updates: http://127.0.0.1:5080");
        
        // Redirect to dashboard
        window.location.href = "http://127.0.0.1:5080";
    }}
    </script>
</body>
</html>'''
    
    # Save the payment page
    os.makedirs('../templates', exist_ok=True)
    with open('../templates/payment_page.html', 'w') as f:
        f.write(html_content)
    
    return payment_link, payment_id

def update_dashboard_for_payment(payment_id, email):
    """Update dashboard to show payment status"""
    
    status_file = '../status/payment_status.json'
    os.makedirs('../status', exist_ok=True)
    
    status = {
        'payment_id': payment_id,
        'user_email': email,
        'amount_usd': 100.00,
        'status': 'pending',
        'timestamp': datetime.now().isoformat(),
        'conversion_status': 'waiting',
        'trading_status': 'ready',
        'dashboard_url': 'http://127.0.0.1:5080'
    }
    
    with open(status_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    return status

if __name__ == '__main__':
    print("Generating Stripe payment link for $100 trading experiment...")
    
    # Load config to get email
    with open('payment_config.json', 'r') as f:
        config = json.load(f)
    
    email = config['user_email']
    
    # Generate payment link
    payment_link, payment_id = generate_payment_link()
    
    # Update dashboard
    status = update_dashboard_for_payment(payment_id, email)
    
    print(f"\n✅ Payment system ready!")
    print(f"📧 User email: {email}")
    print(f"🔗 Payment page: {payment_link}")
    print(f"📊 Dashboard: http://127.0.0.1:5080")
    print(f"\n📋 Payment ID: {payment_id}")
    print(f"💰 Amount: ${status['amount_usd']}")
    print(f"🔄 Status: {status['status']}")
    print(f"\nNext: User clicks payment link → Processes $100 → Trading begins")