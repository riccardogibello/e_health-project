from google_play_scraper import app
from DatabaseManager import insert_id_into_database, do_query

class Application:
    title = None
    description = None
    description_html = None
    summary = None
    summary_html = None
    installs = None
    min_installs = None
    score = None
    ratings = None
    reviews = None
    histogram = None
    price = None
    free = None
    currency = None
    sale = None
    sale_time = None
    original_price = None
    sale_text = None
    offers_IAP = None
    in_app_product_price = None
    size = None
    android_version = None
    android_version_text = None
    developer = None
    developer_id = None
    developer_email = None
    developer_website = None
    developer_address = None
    privacy_policy = None
    developer_internal_id = None
    category = None
    genre_id = None
    icon = None
    header_image = None
    screenshots = None
    video = None
    video_image = None
    content_rating = None
    content_rating_description = None
    ad_supported = None
    contains_ads = None
    released = None
    updated = None
    version = None
    recent_changes = None
    recent_changes_html = None
    comments = None
    editors_choice = None
    similar_apps = None
    more_by_developer = None
    app_id = None
    url = None

    def __init__(self, application_id, online):
        # online is a boolean parameter. If True it will load data from Play Store, if False data will be loaded from local database.
        if online:
            result = app(application_id)
            self.title = result.get('title')
            self.description = result.get('description')
            self.description_html = result.get('descriptionHTML')
            self.summary = result.get('summary')
            self.summary_html = result.get('summaryHTML')
            self.installs = result.get('installs')
            self.min_installs = result.get('minInstalls')
            self.score = result.get('score')
            self.ratings = result.get('ratings')
            self.reviews = result.get('reviews')
            self.histogram = result.get('histogram')
            self.price = result.get('price')
            self.free = result.get('free')
            self.currency = result.get('currency')
            self.sale = result.get('sale')
            self.sale_text = result.get('saleText')
            self.offers_IAP = result.get('offersIAP')
            self.in_app_product_price = result.get('inAppProductPrice')
            self.size = result.get('size')
            self.android_version = result.get('androidVersion')
            self.android_version_text = result.get('androidVersionText')
            self.developer = result.get('developer')
            self.developer_id = result.get('developerId')
            self.developer_email = result.get('developerEmail')
            self.developer_website = result.get('developerWebsite')
            self.developer_address = result.get('developerAddress')
            self.privacy_policy = result.get('privacyPolicy')
            self.developer_internal_id = result.get('developerInternalID')
            self.category = result.get('genre')
            self.genre_id = result.get('genreId')
            self.icon = result.get('icon')
            self.header_image = result.get('headerImage')
            self.screenshots = result.get('screenshots')
            self.video = result.get('video')
            self.video_image = result.get('videoImage')
            self.content_rating = result.get('contentRating')
            self.content_rating_description = result.get('contentRatingDescription')
            self.ad_supported = result.get('adSupported')
            self.contains_ads = result.get('containsAds')
            self.released = result.get('released')
            self.updated = result.get('updated')
            self.version = result.get('version')
            self.recent_changes = result.get('recentChanges')
            self.recent_changes_html = result.get('recentChangesHTML')
            self.comments = result.get('comments')
            self.editors_choice = result.get('editorsChoice')
            self.similar_apps = result.get('similarApps')
            self.more_by_developer = result.get('moreByDeveloper')
            self.app_id = result.get('appId')
            self.url = result.get('url')
            for similar_app in self.similar_apps:
                insert_id_into_database(similar_app)
        else:
            get_query = (
                "SELECT * FROM APP WHERE app_id = %s"
            )
            result_tuple = do_query((application_id,), get_query)
            self.app_id = application_id
            self.title = result_tuple[1]









