"""
Модели базы данных для партнёрской платформы
"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import string

db = SQLAlchemy()


class User(db.Model):
    """Модель пользователя (компания или партнёр)"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # 'company' или 'partner'
    full_name = db.Column(db.String(200))
    company_name = db.Column(db.String(200))
    phone = db.Column(db.String(50))
    balance = db.Column(db.Float, default=0.0)  # Баланс для партнёров
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Связи
    offers = db.relationship('Offer', backref='company', lazy=True)
    affiliate_links = db.relationship('AffiliateLink', backref='partner', lazy=True)
    clicks = db.relationship('Click', backref='partner', lazy=True)
    conversions = db.relationship('Conversion', backref='partner', lazy=True)
    payouts = db.relationship('Payout', backref='partner', lazy=True)

    def set_password(self, password):
        """Установить хешированный пароль"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Проверить пароль"""
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'email': self.email,
            'user_type': self.user_type,
            'full_name': self.full_name,
            'company_name': self.company_name,
            'phone': self.phone,
            'balance': self.balance,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class Offer(db.Model):
    """Модель оффера (товар/услуга от компании)"""
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    product_url = db.Column(db.String(500))
    image_url = db.Column(db.String(500))
    price = db.Column(db.Float, nullable=False)
    commission_percent = db.Column(db.Float, nullable=False)  # % от продажи
    platform_percent = db.Column(db.Float, default=2.0)  # % платформы (по умолчанию 20% от комиссии)
    category = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Связи
    affiliate_links = db.relationship('AffiliateLink', backref='offer', lazy=True)
    clicks = db.relationship('Click', backref='offer', lazy=True)
    conversions = db.relationship('Conversion', backref='offer', lazy=True)

    def calculate_commission(self):
        """Рассчитать комиссию партнёра"""
        total_commission = self.price * (self.commission_percent / 100)
        platform_fee = total_commission * (self.platform_percent / 100)
        partner_commission = total_commission - platform_fee
        return {
            'total_commission': total_commission,
            'partner_commission': partner_commission,
            'platform_fee': platform_fee
        }

    def to_dict(self):
        """Преобразовать в словарь"""
        commission = self.calculate_commission()
        return {
            'id': self.id,
            'company_id': self.company_id,
            'title': self.title,
            'description': self.description,
            'product_url': self.product_url,
            'image_url': self.image_url,
            'price': self.price,
            'commission_percent': self.commission_percent,
            'platform_percent': self.platform_percent,
            'partner_commission': commission['partner_commission'],
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat()
        }


class AffiliateLink(db.Model):
    """Модель партнёрской ссылки"""
    __tablename__ = 'affiliate_links'

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    tracking_code = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Связи
    clicks = db.relationship('Click', backref='affiliate_link', lazy=True)
    conversions = db.relationship('Conversion', backref='affiliate_link', lazy=True)

    @staticmethod
    def generate_tracking_code(length=10):
        """Генерировать уникальный код отслеживания"""
        characters = string.ascii_letters + string.digits
        return ''.join(secrets.choice(characters) for _ in range(length))

    def get_tracking_url(self, base_url):
        """Получить полную ссылку для отслеживания"""
        return f"{base_url}/track/{self.tracking_code}"

    def to_dict(self, base_url=None):
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'offer_id': self.offer_id,
            'tracking_code': self.tracking_code,
            'tracking_url': self.get_tracking_url(base_url) if base_url else None,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active
        }


class Click(db.Model):
    """Модель клика по партнёрской ссылке"""
    __tablename__ = 'clicks'

    id = db.Column(db.Integer, primary_key=True)
    affiliate_link_id = db.Column(db.Integer, db.ForeignKey('affiliate_links.id'), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    referrer = db.Column(db.String(500))
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'affiliate_link_id': self.affiliate_link_id,
            'partner_id': self.partner_id,
            'offer_id': self.offer_id,
            'ip_address': self.ip_address,
            'clicked_at': self.clicked_at.isoformat()
        }


class Conversion(db.Model):
    """Модель конверсии (продажи)"""
    __tablename__ = 'conversions'

    id = db.Column(db.Integer, primary_key=True)
    affiliate_link_id = db.Column(db.Integer, db.ForeignKey('affiliate_links.id'), nullable=False)
    partner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=False)
    order_id = db.Column(db.String(100), unique=True)
    sale_amount = db.Column(db.Float, nullable=False)
    commission_amount = db.Column(db.Float, nullable=False)  # Комиссия партнёра
    platform_fee = db.Column(db.Float, nullable=False)  # Комиссия платформы
    status = db.Column(db.String(50), default='pending')  # pending, approved, rejected, paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime)

    def to_dict(self):
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'affiliate_link_id': self.affiliate_link_id,
            'partner_id': self.partner_id,
            'offer_id': self.offer_id,
            'order_id': self.order_id,
            'sale_amount': self.sale_amount,
            'commission_amount': self.commission_amount,
            'platform_fee': self.platform_fee,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'approved_at': self.approved_at.isoformat() if self.approved_at else None
        }


class Payout(db.Model):
    """Модель выплаты партнёру"""
    __tablename__ = 'payouts'

    id = db.Column(db.Integer, primary_key=True)
    partner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # card, bank_transfer, wallet, etc.
    payment_details = db.Column(db.String(500))
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'partner_id': self.partner_id,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'status': self.status,
            'requested_at': self.requested_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class PasswordReset(db.Model):
    """Модель для восстановления пароля"""
    __tablename__ = 'password_resets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reset_token = db.Column(db.String(100), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_reset_token(length=32):
        """Генерировать уникальный токен для сброса пароля"""
        return secrets.token_urlsafe(length)

    def is_expired(self):
        """Проверить, истёк ли токен"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        """Преобразовать в словарь"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reset_token': self.reset_token,
            'expires_at': self.expires_at.isoformat(),
            'used': self.used,
            'created_at': self.created_at.isoformat()
        }
