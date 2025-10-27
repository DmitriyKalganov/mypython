"""
Главное Flask приложение для партнёрской платформы
"""
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
from datetime import datetime, timedelta
import jwt
import os
from functools import wraps

from .models import db, User, Offer, AffiliateLink, Click, Conversion, Payout

app = Flask(__name__,
            template_folder='../frontend/templates',
            static_folder='../frontend/static')

# Конфигурация
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "affiliate_platform", "database", "affiliate.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализация расширений
db.init_app(app)
CORS(app)

# Middleware для аутентификации
def token_required(f):
    """Декоратор для проверки JWT токена"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[1]

        if not token:
            return jsonify({'error': 'Требуется токен'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'Пользователь не найден'}), 401
        except:
            return jsonify({'error': 'Неверный токен'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# =======================
# Маршруты для страниц
# =======================

@app.route('/')
def index():
    """Главная страница"""
    return render_template('index.html')


@app.route('/login')
def login_page():
    """Страница входа"""
    return render_template('login.html')


@app.route('/register')
def register_page():
    """Страница регистрации"""
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    """Дашборд пользователя"""
    return render_template('dashboard.html')


@app.route('/offers')
def offers_page():
    """Страница офферов"""
    return render_template('offers.html')


# =======================
# API: Аутентификация
# =======================

@app.route('/api/register', methods=['POST'])
def register():
    """Регистрация нового пользователя"""
    data = request.get_json()

    # Проверка обязательных полей
    if not all(k in data for k in ('email', 'password', 'user_type')):
        return jsonify({'error': 'Заполните все обязательные поля'}), 400

    # Проверка существующего пользователя
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 400

    # Создание нового пользователя
    user = User(
        email=data['email'],
        user_type=data['user_type'],
        full_name=data.get('full_name'),
        company_name=data.get('company_name'),
        phone=data.get('phone')
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        'message': 'Регистрация прошла успешно',
        'user': user.to_dict()
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    """Авторизация пользователя"""
    data = request.get_json()

    if not all(k in data for k in ('email', 'password')):
        return jsonify({'error': 'Email и пароль обязательны'}), 400

    user = User.query.filter_by(email=data['email']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Неверный email или пароль'}), 401

    # Генерация JWT токена
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')

    return jsonify({
        'token': token,
        'user': user.to_dict()
    })


# =======================
# API: Офферы
# =======================

@app.route('/api/offers', methods=['GET'])
def get_offers():
    """Получить список офферов"""
    offers = Offer.query.filter_by(is_active=True).all()
    base_url = request.host_url.rstrip('/')
    return jsonify([offer.to_dict() for offer in offers])


@app.route('/api/offers/<int:offer_id>', methods=['GET'])
def get_offer(offer_id):
    """Получить конкретный оффер"""
    offer = Offer.query.get_or_404(offer_id)
    return jsonify(offer.to_dict())


@app.route('/api/offers', methods=['POST'])
@token_required
def create_offer(current_user):
    """Создать новый оффер (только для компаний)"""
    if current_user.user_type != 'company':
        return jsonify({'error': 'Только компании могут создавать офферы'}), 403

    data = request.get_json()

    # Проверка обязательных полей
    required_fields = ['title', 'price', 'commission_percent']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Заполните все обязательные поля'}), 400

    offer = Offer(
        company_id=current_user.id,
        title=data['title'],
        description=data.get('description'),
        product_url=data.get('product_url'),
        image_url=data.get('image_url'),
        price=data['price'],
        commission_percent=data['commission_percent'],
        platform_percent=data.get('platform_percent', 20.0),
        category=data.get('category')
    )

    db.session.add(offer)
    db.session.commit()

    return jsonify({
        'message': 'Оффер успешно создан',
        'offer': offer.to_dict()
    }), 201


@app.route('/api/offers/<int:offer_id>', methods=['PUT'])
@token_required
def update_offer(current_user, offer_id):
    """Обновить оффер"""
    offer = Offer.query.get_or_404(offer_id)

    if offer.company_id != current_user.id:
        return jsonify({'error': 'Нет доступа к этому офферу'}), 403

    data = request.get_json()

    # Обновление полей
    for field in ['title', 'description', 'product_url', 'image_url',
                  'price', 'commission_percent', 'platform_percent', 'category', 'is_active']:
        if field in data:
            setattr(offer, field, data[field])

    db.session.commit()

    return jsonify({
        'message': 'Оффер успешно обновлён',
        'offer': offer.to_dict()
    })


# =======================
# API: Партнёрские ссылки
# =======================

@app.route('/api/affiliate-links', methods=['POST'])
@token_required
def create_affiliate_link(current_user):
    """Создать партнёрскую ссылку"""
    if current_user.user_type != 'partner':
        return jsonify({'error': 'Только партнёры могут создавать ссылки'}), 403

    data = request.get_json()

    if 'offer_id' not in data:
        return jsonify({'error': 'Укажите ID оффера'}), 400

    offer = Offer.query.get_or_404(data['offer_id'])

    # Проверка существующей ссылки
    existing_link = AffiliateLink.query.filter_by(
        partner_id=current_user.id,
        offer_id=offer.id
    ).first()

    if existing_link:
        base_url = request.host_url.rstrip('/')
        return jsonify({
            'message': 'Ссылка уже существует',
            'link': existing_link.to_dict(base_url)
        })

    # Создание новой ссылки
    link = AffiliateLink(
        partner_id=current_user.id,
        offer_id=offer.id,
        tracking_code=AffiliateLink.generate_tracking_code()
    )

    db.session.add(link)
    db.session.commit()

    base_url = request.host_url.rstrip('/')

    return jsonify({
        'message': 'Партнёрская ссылка создана',
        'link': link.to_dict(base_url)
    }), 201


@app.route('/api/affiliate-links', methods=['GET'])
@token_required
def get_affiliate_links(current_user):
    """Получить партнёрские ссылки пользователя"""
    links = AffiliateLink.query.filter_by(partner_id=current_user.id).all()
    base_url = request.host_url.rstrip('/')
    return jsonify([link.to_dict(base_url) for link in links])


# =======================
# API: Трекинг
# =======================

@app.route('/track/<tracking_code>')
def track_click(tracking_code):
    """Отследить клик по партнёрской ссылке"""
    link = AffiliateLink.query.filter_by(tracking_code=tracking_code).first_or_404()

    # Создание записи о клике
    click = Click(
        affiliate_link_id=link.id,
        partner_id=link.partner_id,
        offer_id=link.offer_id,
        ip_address=request.remote_addr,
        user_agent=request.user_agent.string,
        referrer=request.referrer
    )

    db.session.add(click)
    db.session.commit()

    # Редирект на продукт
    offer = Offer.query.get(link.offer_id)
    if offer.product_url:
        return redirect(offer.product_url)
    else:
        return redirect(url_for('offers_page'))


@app.route('/api/conversions', methods=['POST'])
@token_required
def create_conversion(current_user):
    """Создать конверсию (продажу)"""
    data = request.get_json()

    required_fields = ['affiliate_link_id', 'sale_amount']
    if not all(k in data for k in required_fields):
        return jsonify({'error': 'Заполните все обязательные поля'}), 400

    link = AffiliateLink.query.get_or_404(data['affiliate_link_id'])
    offer = Offer.query.get(link.offer_id)

    # Расчёт комиссий
    commission = offer.calculate_commission()

    conversion = Conversion(
        affiliate_link_id=link.id,
        partner_id=link.partner_id,
        offer_id=link.offer_id,
        order_id=data.get('order_id'),
        sale_amount=data['sale_amount'],
        commission_amount=commission['partner_commission'],
        platform_fee=commission['platform_fee']
    )

    db.session.add(conversion)
    db.session.commit()

    return jsonify({
        'message': 'Конверсия зарегистрирована',
        'conversion': conversion.to_dict()
    }), 201


# =======================
# API: Статистика
# =======================

@app.route('/api/stats/partner', methods=['GET'])
@token_required
def get_partner_stats(current_user):
    """Получить статистику партнёра"""
    if current_user.user_type != 'partner':
        return jsonify({'error': 'Только для партнёров'}), 403

    # Клики
    total_clicks = Click.query.filter_by(partner_id=current_user.id).count()

    # Конверсии
    conversions = Conversion.query.filter_by(partner_id=current_user.id).all()
    total_conversions = len(conversions)

    # Заработок
    total_earnings = sum(c.commission_amount for c in conversions if c.status == 'approved')
    pending_earnings = sum(c.commission_amount for c in conversions if c.status == 'pending')

    # Конверсионная способность
    conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0

    return jsonify({
        'total_clicks': total_clicks,
        'total_conversions': total_conversions,
        'conversion_rate': round(conversion_rate, 2),
        'total_earnings': total_earnings,
        'pending_earnings': pending_earnings,
        'balance': current_user.balance,
        'recent_conversions': [c.to_dict() for c in conversions[-10:]]
    })


@app.route('/api/stats/company', methods=['GET'])
@token_required
def get_company_stats(current_user):
    """Получить статистику компании"""
    if current_user.user_type != 'company':
        return jsonify({'error': 'Только для компаний'}), 403

    # Офферы компании
    offers = Offer.query.filter_by(company_id=current_user.id).all()
    offer_ids = [o.id for o in offers]

    # Клики по офферам
    total_clicks = Click.query.filter(Click.offer_id.in_(offer_ids)).count()

    # Конверсии
    conversions = Conversion.query.filter(Conversion.offer_id.in_(offer_ids)).all()
    total_conversions = len(conversions)
    total_sales = sum(c.sale_amount for c in conversions)

    # Партнёры
    unique_partners = len(set(c.partner_id for c in conversions))

    return jsonify({
        'total_offers': len(offers),
        'total_clicks': total_clicks,
        'total_conversions': total_conversions,
        'total_sales': total_sales,
        'unique_partners': unique_partners,
        'recent_conversions': [c.to_dict() for c in conversions[-10:]]
    })


# =======================
# API: Выплаты
# =======================

@app.route('/api/payouts', methods=['POST'])
@token_required
def request_payout(current_user):
    """Запросить выплату"""
    if current_user.user_type != 'partner':
        return jsonify({'error': 'Только для партнёров'}), 403

    data = request.get_json()

    if 'amount' not in data or data['amount'] <= 0:
        return jsonify({'error': 'Укажите корректную сумму'}), 400

    if data['amount'] > current_user.balance:
        return jsonify({'error': 'Недостаточно средств на балансе'}), 400

    payout = Payout(
        partner_id=current_user.id,
        amount=data['amount'],
        payment_method=data.get('payment_method'),
        payment_details=data.get('payment_details')
    )

    db.session.add(payout)
    db.session.commit()

    return jsonify({
        'message': 'Запрос на выплату создан',
        'payout': payout.to_dict()
    }), 201


@app.route('/api/payouts', methods=['GET'])
@token_required
def get_payouts(current_user):
    """Получить историю выплат"""
    payouts = Payout.query.filter_by(partner_id=current_user.id).all()
    return jsonify([p.to_dict() for p in payouts])


# =======================
# Инициализация БД
# =======================

@app.cli.command()
def init_db():
    """Инициализировать базу данных"""
    db.create_all()
    print('База данных инициализирована!')


@app.cli.command()
def seed_db():
    """Заполнить БД тестовыми данными"""
    # Создание тестовой компании
    company = User(
        email='company@example.com',
        user_type='company',
        full_name='Тестовая Компания',
        company_name='Tech Solutions LLC',
        phone='+998901234567'
    )
    company.set_password('password123')
    db.session.add(company)
    db.session.commit()

    # Создание тестового партнёра
    partner = User(
        email='partner@example.com',
        user_type='partner',
        full_name='Иван Иванов',
        phone='+998909876543'
    )
    partner.set_password('password123')
    db.session.add(partner)
    db.session.commit()

    # Создание тестовых офферов
    offers_data = [
        {
            'title': 'Курс по программированию Python',
            'description': 'Полный курс Python от начального до продвинутого уровня',
            'price': 500000,
            'commission_percent': 15,
            'category': 'Образование'
        },
        {
            'title': 'Смартфон Samsung Galaxy A54',
            'description': 'Современный смартфон с отличной камерой',
            'price': 3500000,
            'commission_percent': 10,
            'category': 'Электроника'
        },
        {
            'title': 'Фитнес-подписка на 3 месяца',
            'description': 'Безлимитное посещение тренажёрного зала',
            'price': 600000,
            'commission_percent': 20,
            'category': 'Здоровье'
        }
    ]

    for offer_data in offers_data:
        offer = Offer(company_id=company.id, **offer_data)
        db.session.add(offer)

    db.session.commit()
    print('База данных заполнена тестовыми данными!')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
