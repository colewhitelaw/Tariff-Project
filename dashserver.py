from app import app

# Import required app pages to ensure they're registered
import pages.global_trends
import pages.business_analytics
import pages.tariff_trends
import pages.home
import pages.about
import pages.state_analysis
import pages.country_analysis

# This file is imported by index.py to ensure all pages are properly loaded 