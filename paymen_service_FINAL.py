import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """Handle payment processing"""
    
    def __init__(self):
        self.click_api_url = "https://api.click.uz/v2"
        self.payme_api_url = "https://checkout.paycom.uz/api"
    
    def get_payment_link(self, user_id, amount, currency, gateway):
        """Get payment link for specified gateway"""
        try:
            logger.info(f"Payment requested: {amount} {currency} via {gateway}")
            
            if gateway == "click":
                return f"https://click.uz/services/pay?amount={amount}"
            elif gateway == "payme":
                return f"https://checkout.paycom.uz/?amount={amount}"
            else:
                logger.error(f"Unknown gateway: {gateway}")
                return None
        
        except Exception as e:
            logger.error(f"Error getting payment link: {e}")
            return None
