"""Add diaries table

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
