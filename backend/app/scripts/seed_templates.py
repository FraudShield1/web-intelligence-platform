"""Seed script to populate platform templates"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models import PlatformTemplate
from app.config import settings
import uuid

# Template definitions
TEMPLATES = [
    {
        "platform_name": "shopify",
        "platform_variant": None,
        "confidence": 0.95,
        "match_patterns": {
            "indicators": ["Shopify.AppBridge", "myshopify.com", "cdn.shopify.com"],
            "header_indicators": {
                "x-shopify-stage": "production"
            }
        },
        "category_selectors": {
            "nav_menu": ".nav-menu, .site-nav, nav[role='navigation']",
            "category_link": "a[href*='/collections/'], a[href*='/categories/']",
            "breadcrumb": ".breadcrumb, nav[aria-label='Breadcrumb']"
        },
        "product_list_selectors": {
            "container": ".product-grid, .product-list, [data-product-id]",
            "product_item": ".product-item, .grid-product, .product-card",
            "product_link": "a[href*='/products/']",
            "product_title": ".product-title, h2, .product-name",
            "product_price": ".price, .product-price, [data-price]",
            "product_image": "img[src*='products'], .product-image img"
        },
        "api_patterns": {
            "endpoints": [
                {
                    "url": "/api/products.json",
                    "method": "GET",
                    "params": ["page", "limit", "collection_id"],
                    "type": "REST"
                },
                {
                    "url": "/api/customers.json",
                    "method": "GET",
                    "type": "REST"
                }
            ],
            "graphql_endpoint": "/graphql.json"
        },
        "render_hints": {
            "requires_js": False,
            "wait_for_selector": ".product-grid",
            "timeout_seconds": 10
        }
    },
    {
        "platform_name": "magento",
        "platform_variant": "2.x",
        "confidence": 0.92,
        "match_patterns": {
            "indicators": ["Magento_Js", "mage", "require.js", "Magento/v2"],
            "header_indicators": {}
        },
        "category_selectors": {
            "nav_menu": ".navigation, .nav, .main-menu",
            "category_link": "a[href*='/category/'], a[href*='/catalog/']",
            "breadcrumb": ".breadcrumbs, .breadcrumb"
        },
        "product_list_selectors": {
            "container": ".products-grid, .products-list, .product-items",
            "product_item": ".product-item, .product-item-info",
            "product_link": "a[href*='/product/'], a.product-item-link",
            "product_title": ".product-item-name, .product-name",
            "product_price": ".price, .price-box, .price-final",
            "product_image": ".product-image img, .product-image-photo"
        },
        "api_patterns": {
            "endpoints": [
                {
                    "url": "/rest/default/V1/products",
                    "method": "GET",
                    "params": ["searchCriteria"],
                    "type": "REST"
                }
            ]
        },
        "render_hints": {
            "requires_js": True,
            "wait_for_selector": ".product-items",
            "timeout_seconds": 15
        }
    },
    {
        "platform_name": "woocommerce",
        "platform_variant": None,
        "confidence": 0.88,
        "match_patterns": {
            "indicators": ["wp-content", "woocommerce", "wc-", "WooCommerce"],
            "header_indicators": {}
        },
        "category_selectors": {
            "nav_menu": ".woocommerce-products-header, .woocommerce-breadcrumb",
            "category_link": "a[href*='/product-category/'], a[href*='/shop/']",
            "breadcrumb": ".woocommerce-breadcrumb"
        },
        "product_list_selectors": {
            "container": ".products, .woocommerce-products, ul.products",
            "product_item": ".product, li.product, .product-item",
            "product_link": "a[href*='/product/'], .woocommerce-loop-product__link",
            "product_title": ".woocommerce-loop-product__title, h2, .product-title",
            "product_price": ".price, .woocommerce-Price-amount",
            "product_image": ".wp-post-image, .product-image img"
        },
        "api_patterns": {
            "endpoints": [
                {
                    "url": "/wp-json/wc/v3/products",
                    "method": "GET",
                    "params": ["page", "per_page", "category"],
                    "type": "REST",
                    "auth": "basic"
                }
            ]
        },
        "render_hints": {
            "requires_js": False,
            "wait_for_selector": ".products",
            "timeout_seconds": 10
        }
    },
    {
        "platform_name": "bigcommerce",
        "platform_variant": None,
        "confidence": 0.89,
        "match_patterns": {
            "indicators": ["bigcommerce", "storefront", "stencil"],
            "header_indicators": {}
        },
        "category_selectors": {
            "nav_menu": ".navPages-list, .navPages",
            "category_link": "a[href*='/category/']",
            "breadcrumb": ".breadcrumbs"
        },
        "product_list_selectors": {
            "container": ".productGrid, .product-list",
            "product_item": ".product, .product-item",
            "product_link": "a[href*='/products/']",
            "product_title": ".product-title, .card-title",
            "product_price": ".price, .price-section",
            "product_image": ".product-image img, .card-image img"
        },
        "api_patterns": {
            "endpoints": [
                {
                    "url": "/api/v3/catalog/products",
                    "method": "GET",
                    "params": ["page", "limit", "categories"],
                    "type": "REST",
                    "auth": "oauth"
                }
            ]
        },
        "render_hints": {
            "requires_js": True,
            "wait_for_selector": ".productGrid",
            "timeout_seconds": 12
        }
    }
]


async def seed_templates():
    """Seed platform templates into database"""
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as db:
        print("🌱 Seeding platform templates...")
        
        for template_data in TEMPLATES:
            # Check if template already exists
            from sqlalchemy import select
            stmt = select(PlatformTemplate).where(
                PlatformTemplate.platform_name == template_data["platform_name"],
                PlatformTemplate.platform_variant == template_data.get("platform_variant")
            )
            result = await db.execute(stmt)
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"  ⏭️  Template {template_data['platform_name']} already exists, skipping")
                continue
            
            # Create new template
            template = PlatformTemplate(
                template_id=uuid.uuid4(),
                platform_name=template_data["platform_name"],
                platform_variant=template_data.get("platform_variant"),
                category_selectors=template_data.get("category_selectors"),
                product_list_selectors=template_data.get("product_list_selectors"),
                api_patterns=template_data.get("api_patterns"),
                render_hints=template_data.get("render_hints"),
                confidence=template_data.get("confidence"),
                active=True,
                match_patterns=template_data.get("match_patterns")
            )
            
            db.add(template)
            print(f"  ✅ Created template: {template_data['platform_name']}")
        
        await db.commit()
        print("✅ Template seeding complete!")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_templates())

