# apps/publications/management/commands/sync_publications.py
from django.core.management.base import BaseCommand
from django.db import transaction
from django.conf import settings
import requests
import time
from datetime import datetime, timedelta

from apps.publications.models import (
    Publication, Author, Venue, CitationMetric, LabPublicationStats
)


class Command(BaseCommand):
    help = 'Sync publication data from external sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            choices=['google_scholar', 'semantic_scholar', 'crossref', 'all'],
            default='all',
            help='Data source to sync from'
        )
        parser.add_argument(
            '--update-citations',
            action='store_true',
            help='Update citation counts for existing publications'
        )
        parser.add_argument(
            '--lab-id',
            type=int,
            help='Sync publications for specific lab only'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if recently updated'
        )

    def handle(self, *args, **options):
        self.stdout.write('🔄 Starting publication sync...')

        source = options['source']
        update_citations = options['update_citations']
        lab_id = options.get('lab_id')
        force = options['force']

        try:
            if source == 'all':
                self.sync_google_scholar(lab_id, force)
                self.sync_semantic_scholar(lab_id, force)
                if update_citations:
                    self.update_citation_metrics(lab_id, force)
            elif source == 'google_scholar':
                self.sync_google_scholar(lab_id, force)
            elif source == 'semantic_scholar':
                self.sync_semantic_scholar(lab_id, force)
            elif source == 'crossref':
                self.sync_crossref(lab_id, force)

            if update_citations:
                self.update_citation_metrics(lab_id, force)

            # Update lab statistics
            self.update_lab_statistics(lab_id)

            self.stdout.write(
                self.style.SUCCESS('✅ Publication sync completed successfully!')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Sync failed: {str(e)}')
            )
            raise e

    def sync_google_scholar(self, lab_id=None, force=False):
        """Google Scholar에서 논문 데이터 동기화"""
        self.stdout.write('📚 Syncing from Google Scholar...')

        # TODO: Google Scholar API 연동 구현
        # 현재는 더미 구현
        self.stdout.write('⚠️ Google Scholar sync not implemented yet')

    def sync_semantic_scholar(self, lab_id=None, force=False):
        """Semantic Scholar API에서 논문 데이터 동기화"""
        self.stdout.write('🔬 Syncing from Semantic Scholar...')

        try:
            # 기존 논문들의 DOI 수집
            publications = Publication.objects.exclude(doi='')
            if lab_id:
                publications = publications.filter(labs=lab_id)

            updated_count = 0
            for pub in publications:
                if self.update_from_semantic_scholar(pub, force):
                    updated_count += 1
                    if updated_count % 10 == 0:
                        self.stdout.write(f'   Updated {updated_count} publications...')

                # API 제한을 위한 딜레이
                time.sleep(0.1)

            self.stdout.write(f'✅ Updated {updated_count} publications from Semantic Scholar')

        except Exception as e:
            self.stdout.write(f'❌ Semantic Scholar sync error: {str(e)}')

    def update_from_semantic_scholar(self, publication, force=False):
        """Semantic Scholar API에서 단일 논문 정보 업데이트"""
        if not publication.doi and not force:
            return False

        # 최근에 업데이트되었으면 스킵 (force가 아닌 경우)
        if not force and publication.updated_at > datetime.now() - timedelta(days=7):
            return False

        try:
            # Semantic Scholar API 호출
            if publication.doi:
                url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{publication.doi}"
            else:
                # 제목으로 검색
                search_url = f"https://api.semanticscholar.org/graph/v1/paper/search"
                params = {'query': publication.title, 'limit': 1}
                response = requests.get(search_url, params=params, timeout=10)
                if response.status_code != 200:
                    return False

                data = response.json()
                if not data.get('data'):
                    return False

                paper_id = data['data'][0]['paperId']
                url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}"

            # 논문 상세 정보 요청
            params = {
                'fields': 'title,abstract,year,citationCount,influentialCitationCount,authors,venue,url'
            }
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # 논문 정보 업데이트
                updated = False

                if data.get('citationCount') and data['citationCount'] != publication.citation_count:
                    publication.citation_count = data['citationCount']
                    updated = True

                if data.get('abstract') and not publication.abstract:
                    publication.abstract = data['abstract']
                    updated = True

                if data.get('url') and not publication.paper_url:
                    publication.paper_url = data['url']
                    updated = True

                if updated:
                    publication.save()

                # 인용 메트릭 기록
                CitationMetric.objects.create(
                    publication=publication,
                    citation_count=data.get('citationCount', 0),
                    influential_citation_count=data.get('influentialCitationCount', 0),
                    source='semantic_scholar'
                )

                return updated

        except requests.RequestException as e:
            self.stdout.write(f'⚠️ API request failed for {publication.title[:50]}: {str(e)}')
        except Exception as e:
            self.stdout.write(f'⚠️ Error updating {publication.title[:50]}: {str(e)}')

        return False

    def sync_crossref(self, lab_id=None, force=False):
        """CrossRef에서 논문 메타데이터 동기화"""
        self.stdout.write('📖 Syncing from CrossRef...')

        # TODO: CrossRef API 연동 구현
        self.stdout.write('⚠️ CrossRef sync not implemented yet')

    def update_citation_metrics(self, lab_id=None, force=False):
        """인용 메트릭 업데이트"""
        self.stdout.write('📊 Updating citation metrics...')

        publications = Publication.objects.all()
        if lab_id:
            publications = publications.filter(labs=lab_id)

        # 최근 1주일 동안 업데이트되지 않은 논문들만 처리
        if not force:
            one_week_ago = datetime.now() - timedelta(days=7)
            publications = publications.filter(
                citationmetric__recorded_at__lt=one_week_ago
            ).distinct()

        updated_count = 0
        for pub in publications:
            if self.update_from_semantic_scholar(pub, force):
                updated_count += 1

        self.stdout.write(f'✅ Updated citation metrics for {updated_count} publications')

    def update_lab_statistics(self, lab_id=None):
        """연구실 통계 업데이트"""
        self.stdout.write('📈 Updating lab statistics...')

        from apps.labs.models import Lab
        from django.db.models import Count, Sum, Avg

        labs = Lab.objects.all()
        if lab_id:
            labs = labs.filter(id=lab_id)

        updated_count = 0
        for lab in labs:
            # 기본 통계 계산
            pub_stats = lab.publications.aggregate(
                total_pubs=Count('id'),
                total_citations=Sum('citation_count'),
                avg_citations=Avg('citation_count')
            )

            # 최근 5년 논문 수
            current_year = datetime.now().year
            recent_pubs = lab.publications.filter(
                publication_year__gte=current_year - 5
            ).count()

            # 탑티어 논문 수
            top_tier_count = lab.publications.filter(
                venues__tier='top'
            ).count()

            # 가장 많이 인용된 논문
            most_cited = lab.publications.order_by('-citation_count').first()

            # H-index 계산 (간단한 구현)
            citations = list(
                lab.publications.values_list('citation_count', flat=True).order_by('-citation_count')
            )
            h_index = 0
            for i, citations_count in enumerate(citations, 1):
                if citations_count >= i:
                    h_index = i
                else:
                    break

            # 통계 업데이트 또는 생성
            stats, created = LabPublicationStats.objects.update_or_create(
                lab=lab,
                defaults={
                    'total_publications': pub_stats['total_pubs'] or 0,
                    'total_citations': pub_stats['total_citations'] or 0,
                    'h_index': h_index,
                    'avg_citations_per_paper': pub_stats['avg_citations'] or 0.0,
                    'publications_last_5_years': recent_pubs,
                    'top_tier_count': top_tier_count,
                    'most_cited_paper': most_cited,
                }
            )

            updated_count += 1

        self.stdout.write(f'✅ Updated statistics for {updated_count} labs')

    def handle_api_rate_limit(self, wait_time=1):
        """API 속도 제한 처리"""
        time.sleep(wait_time)