#!/usr/bin/env python3
"""
Google Scholar Scraper with Backend REST API Integration
For use with GitHub Actions, Render Cron Jobs, or Railway
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime
from scholarly import scholarly
from typing import List, Dict, Optional

# logs 디렉토리 생성 (로깅 설정보다 먼저 실행)
os.makedirs('logs', exist_ok=True)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 환경변수
BACKEND_API_URL = os.getenv('BACKEND_API_URL', 'http://localhost:3000')
API_TOKEN = os.getenv('API_TOKEN', '')
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL', '')
PROFESSOR_LIMIT = int(os.getenv('PROFESSOR_LIMIT', '10'))
MAX_PUBLICATIONS = int(os.getenv('MAX_PUBLICATIONS', '50'))


class ScholarScraper:
    def __init__(self):
        self.headers = {
            'Authorization': f'Bearer {API_TOKEN}',
            'Content-Type': 'application/json'
        }
        self.stats = {
            'total_professors': 0,
            'successful': 0,
            'failed': 0,
            'total_publications': 0
        }

    @staticmethod
    def extract_scholar_id(google_scholar_url: str) -> Optional[str]:
        """Google Scholar URL에서 scholar_id 추출

        Examples:
            https://scholar.google.com/citations?user=ABC123&hl=en -> ABC123
            https://scholar.google.co.kr/citations?user=XYZ789 -> XYZ789
        """
        if not google_scholar_url:
            return None

        try:
            # URL에서 user= 파라미터 값 추출
            if 'user=' in google_scholar_url:
                scholar_id = google_scholar_url.split('user=')[1].split('&')[0]
                return scholar_id.strip() if scholar_id else None
        except Exception as e:
            logger.warning(f"⚠️  Failed to extract scholar_id from URL: {google_scholar_url} - {e}")

        return None

    def get_professors(self) -> List[Dict]:
        """Backend API에서 교수 목록 가져오기"""
        try:
            url = f"{BACKEND_API_URL}/api/v1/professors/"
            # Get professors with scholar_id set (filter in Python since API doesn't support this filter)
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            # Handle paginated response
            if isinstance(data, dict) and 'results' in data:
                all_professors = data['results']
            elif isinstance(data, list):
                all_professors = data
            else:
                logger.error(f"❌ Unexpected API response format: {type(data)}")
                return []

            logger.info(f"📊 Total professors from API: {len(all_professors)}")

            # Filter for professors with google_scholar_url (non-empty string)
            professors = [p for p in all_professors if p.get('google_scholar_url', '').strip()][:PROFESSOR_LIMIT]

            logger.info(f"✅ Fetched {len(professors)} professors with google_scholar_url from API")

            # Debug: Show Google Scholar URLs found
            if professors:
                for p in professors[:5]:  # Show first 5
                    url = p.get('google_scholar_url', 'N/A')
                    scholar_id = self.extract_scholar_id(url)
                    logger.info(f"  - {p.get('name', 'Unknown')}: {url} (ID: {scholar_id})")

            return professors

        except Exception as e:
            logger.error(f"❌ Failed to fetch professors: {e}")
            return []

    def scrape_professor_publications(self, scholar_id: str) -> Optional[Dict]:
        """Google Scholar에서 논문 정보 수집"""
        try:
            logger.info(f"🔍 Scraping scholar_id: {scholar_id}")
            start_time = time.time()

            # 교수 정보 검색
            author = scholarly.search_author_id(scholar_id)
            author_info = scholarly.fill(author, sections=['basics', 'publications'])

            publications = []

            # 논문 정보 수집
            for idx, pub in enumerate(author_info.get('publications', [])[:MAX_PUBLICATIONS]):
                try:
                    filled_pub = scholarly.fill(pub)

                    publication = {
                        'title': filled_pub.get('bib', {}).get('title', ''),
                        'authors': filled_pub.get('bib', {}).get('author', '').split(' and '),
                        'year': filled_pub.get('bib', {}).get('pub_year'),
                        'citations': filled_pub.get('num_citations', 0),
                        'venue': filled_pub.get('bib', {}).get('venue', ''),
                        'pub_url': filled_pub.get('pub_url', ''),
                        'scholar_url': filled_pub.get('scholar_url', ''),
                        'abstract': filled_pub.get('bib', {}).get('abstract', ''),
                        'bib': filled_pub.get('bib', {})
                    }

                    publications.append(publication)

                    # Rate limiting
                    time.sleep(2)

                except Exception as e:
                    logger.warning(f"⚠️  Failed to fetch publication {idx}: {e}")
                    continue

            execution_time = int(time.time() - start_time)

            result = {
                'publications': publications,
                'metadata': {
                    'scholar_id': scholar_id,
                    'name': author_info.get('name', ''),
                    'affiliation': author_info.get('affiliation', ''),
                    'total_citations': author_info.get('citedby', 0),
                    'h_index': author_info.get('hindex', 0),
                    'i10_index': author_info.get('i10index', 0),
                    'publications_count': len(publications),
                    'execution_time_seconds': execution_time,
                    'scraped_at': datetime.utcnow().isoformat()
                }
            }

            logger.info(f"✅ Scraped {len(publications)} publications in {execution_time}s")
            return result

        except Exception as e:
            logger.error(f"❌ Failed to scrape {scholar_id}: {e}")
            return None

    def save_publications(self, professor_id: int, data: Dict) -> bool:
        """Backend API로 논문 데이터 저장"""
        try:
            url = f"{BACKEND_API_URL}/api/v1/publications/bulk_import_from_scholar/"
            payload = {
                'professor_id': professor_id,
                'publications': data['publications']
            }

            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()

            result = response.json()
            logger.info(f"✅ Saved publications: created={result.get('created')}, updated={result.get('updated')}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to save publications: {e}")
            return False

    def log_scraping_result(self, professor_id: int, status: str,
                           publications_count: int = 0,
                           error_message: str = None,
                           execution_time: int = 0):
        """스크래핑 결과 로깅"""
        try:
            url = f"{BACKEND_API_URL}/api/v1/publications/scraping-logs/"
            payload = {
                'professor_id': professor_id,
                'status': status,
                'publications_count': publications_count,
                'execution_time_seconds': execution_time,
                'error_message': error_message
            }

            requests.post(url, headers=self.headers, json=payload, timeout=30)

        except Exception as e:
            logger.warning(f"⚠️  Failed to log result: {e}")

    def process_professor(self, professor: Dict):
        """단일 교수 처리"""
        professor_id = professor['id']
        professor_name = professor['name']
        google_scholar_url = professor.get('google_scholar_url', '')

        # Google Scholar URL에서 scholar_id 추출
        scholar_id = self.extract_scholar_id(google_scholar_url)

        if not scholar_id:
            logger.warning(f"⚠️  Professor {professor_name} has no valid scholar_id in URL: {google_scholar_url}")
            return

        logger.info(f"📚 Processing: {professor_name} ({professor.get('university_name', 'Unknown')}) - Scholar ID: {scholar_id}")

        # Google Scholar 스크래핑
        scraped_data = self.scrape_professor_publications(scholar_id)

        if scraped_data:
            # 데이터 저장
            if self.save_publications(professor_id, scraped_data):
                self.stats['successful'] += 1
                self.stats['total_publications'] += scraped_data['metadata']['publications_count']

                self.log_scraping_result(
                    professor_id=professor_id,
                    status='success',
                    publications_count=scraped_data['metadata']['publications_count'],
                    execution_time=scraped_data['metadata']['execution_time_seconds']
                )
            else:
                self.stats['failed'] += 1
                self.log_scraping_result(
                    professor_id=professor_id,
                    status='failed',
                    error_message='Failed to save to API'
                )
        else:
            self.stats['failed'] += 1
            self.log_scraping_result(
                professor_id=professor_id,
                status='failed',
                error_message='Failed to scrape Google Scholar'
            )

    def send_summary_notification(self):
        """작업 완료 알림 전송"""
        if not SLACK_WEBHOOK_URL:
            return

        try:
            message = {
                "text": "📊 Scholar Scraping Summary",
                "attachments": [{
                    "color": "good" if self.stats['failed'] == 0 else "warning",
                    "fields": [
                        {"title": "Total Professors", "value": str(self.stats['total_professors']), "short": True},
                        {"title": "Successful", "value": str(self.stats['successful']), "short": True},
                        {"title": "Failed", "value": str(self.stats['failed']), "short": True},
                        {"title": "Total Publications", "value": str(self.stats['total_publications']), "short": True}
                    ]
                }]
            }

            requests.post(SLACK_WEBHOOK_URL, json=message, timeout=10)
            logger.info("✅ Sent summary notification")

        except Exception as e:
            logger.warning(f"⚠️  Failed to send notification: {e}")

    def run(self):
        """메인 실행 함수"""
        logger.info("=" * 60)
        logger.info("🚀 Starting Google Scholar Scraper")
        logger.info("=" * 60)
        logger.info(f"📍 Backend API URL: {BACKEND_API_URL}")
        logger.info(f"📍 Professor Limit: {PROFESSOR_LIMIT}")
        logger.info(f"📍 Max Publications: {MAX_PUBLICATIONS}")
        logger.info("=" * 60)

        # 교수 목록 가져오기
        professors = self.get_professors()
        self.stats['total_professors'] = len(professors)

        if not professors:
            logger.warning("⚠️  No professors to process")
            return

        # 각 교수 처리
        for idx, professor in enumerate(professors, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing {idx}/{len(professors)}")
            logger.info(f"{'='*60}")

            self.process_professor(professor)

            # Rate limiting between professors
            if idx < len(professors):
                time.sleep(5)

        # 최종 통계
        logger.info("\n" + "=" * 60)
        logger.info("📊 Scraping Summary")
        logger.info("=" * 60)
        logger.info(f"Total Professors: {self.stats['total_professors']}")
        logger.info(f"Successful: {self.stats['successful']}")
        logger.info(f"Failed: {self.stats['failed']}")
        logger.info(f"Total Publications: {self.stats['total_publications']}")
        logger.info("=" * 60)

        # 알림 전송
        self.send_summary_notification()


if __name__ == '__main__':
    try:
        scraper = ScholarScraper()
        scraper.run()

        # 실패가 있으면 exit code 1
        if scraper.stats['failed'] > 0:
            sys.exit(1)

    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)
