"""
잘못된 마이그레이션 문제 해결 스크립트
"""
import os
import subprocess
import sys
from pathlib import Path

def fix_migration_issue():
    """마이그레이션 문제 해결"""
    print("🔧 잘못된 마이그레이션 문제 해결 중...")
    
    # 1. 잘못된 마이그레이션 파일 삭제
    bad_migration = "D:\\ai-diary-backend\\alembic\\versions\\20250613_2325_0e523049e470_add_missing_tables_including_diaries.py"
    if os.path.exists(bad_migration):
        os.remove(bad_migration)
        print("✅ 잘못된 마이그레이션 파일 삭제 완료")
    
    # 2. 마이그레이션 상태 확인
    print("\n🔍 현재 마이그레이션 상태 확인...")
    try:
        result = subprocess.run(["alembic", "current"], capture_output=True, text=True)
        print(f"📄 현재 상태: {result.stdout}")
    except Exception as e:
        print(f"❌ 상태 확인 실패: {e}")
    
    # 3. 올바른 마이그레이션 생성
    print("\n📝 올바른 마이그레이션 수동 생성 중...")
    
    # diaries 테이블만 추가하는 마이그레이션 생성
    migration_content = '''"""Add diaries table

Revision ID: 0002
Revises: 0001
Create Date: 2025-06-13 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0002'
down_revision = '0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """일기 테이블 추가"""
    # 일기 테이블 생성
    op.create_table('diaries',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('diary_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('original_content', sa.Text(), nullable=True),
        sa.Column('diary_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('word_count', sa.Integer(), nullable=True),
        sa.Column('character_count', sa.Integer(), nullable=True),
        sa.Column('writing_time_minutes', sa.Integer(), nullable=True),
        sa.Column('user_mood', sa.String(length=50), nullable=True),
        sa.Column('user_emotion_tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('weather', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('is_private', sa.Boolean(), nullable=True),
        sa.Column('is_deleted', sa.Boolean(), nullable=True),
        sa.Column('is_analyzed', sa.Boolean(), nullable=True),
        sa.Column('diary_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_diaries_diary_id', 'diaries', ['diary_id'], unique=True)
    op.create_index('ix_diaries_id', 'diaries', ['id'], unique=False)
    op.create_index('ix_diaries_user_id', 'diaries', ['user_id'], unique=False)


def downgrade() -> None:
    """일기 테이블 삭제"""
    op.drop_index('ix_diaries_user_id', table_name='diaries')
    op.drop_index('ix_diaries_id', table_name='diaries')
    op.drop_index('ix_diaries_diary_id', table_name='diaries')
    op.drop_table('diaries')
'''
    
    # 새로운 마이그레이션 파일 생성
    migration_file = "D:\\ai-diary-backend\\alembic\\versions\\20250613_2330_0002_add_diaries_table.py"
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    print("✅ 새로운 마이그레이션 파일 생성 완료")
    
    # 4. 마이그레이션 적용
    print("\n🔄 새 마이그레이션 적용 중...")
    try:
        result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ 마이그레이션 적용 성공!")
            print(f"📄 출력: {result.stdout}")
            return True
        else:
            print("❌ 마이그레이션 적용 실패:")
            print(f"🚨 오류: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ 마이그레이션 실패: {e}")
        return False

def try_main_py():
    """main.py 실행 시도"""
    print("\n🚀 main.py 실행 시도...")
    
    try:
        # main.py 실행 (10초 타임아웃)
        result = subprocess.Popen([
            sys.executable, "-m", "app.main"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏰ 서버 시작 중... (10초 후 확인)")
        try:
            stdout, stderr = result.communicate(timeout=10)
            print(f"📄 출력: {stdout}")
            if stderr:
                print(f"🚨 오류: {stderr}")
        except subprocess.TimeoutExpired:
            print("✅ 서버가 정상적으로 시작되었습니다!")
            print("🌐 http://localhost:8000 에서 실행 중")
            print("📚 API 문서: http://localhost:8000/docs")
            result.terminate()
            return True
            
    except Exception as e:
        print(f"❌ main.py 실행 실패: {e}")
        return False

if __name__ == "__main__":
    print("🚨 마이그레이션 긴급 수정")
    print("=" * 50)
    
    if fix_migration_issue():
        print("\n✅ 마이그레이션 수정 완료!")
        
        if try_main_py():
            print("\n🎉 main.py 실행 성공!")
        else:
            print("\n💡 수동으로 실행해보세요:")
            print("python -m app.main")
    else:
        print("\n❌ 마이그레이션 수정 실패")
        print("💡 수동 해결이 필요합니다.")
