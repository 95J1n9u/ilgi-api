"""Initial database schema

Revision ID: 0001
Revises: 
Create Date: 2024-12-12 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """업그레이드 마이그레이션"""
    # 사용자 테이블 생성
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('firebase_uid', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('picture', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('age', sa.Integer(), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('settings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('preferences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=True),
        sa.Column('email_verified', sa.Boolean(), nullable=True),
        sa.Column('matching_enabled', sa.Boolean(), nullable=True),
        sa.Column('profile_visibility', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_firebase_uid'), 'users', ['firebase_uid'], unique=True)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=False)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # 일기 분석 결과 테이블 생성
    op.create_table('diary_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('analysis_id', sa.String(length=255), nullable=False),
        sa.Column('diary_id', sa.String(length=255), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('content_length', sa.Integer(), nullable=True),
        sa.Column('emotions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('primary_emotion', sa.String(length=50), nullable=True),
        sa.Column('secondary_emotions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sentiment_score', sa.Float(), nullable=True),
        sa.Column('emotional_intensity', sa.Float(), nullable=True),
        sa.Column('emotional_stability', sa.Float(), nullable=True),
        sa.Column('personality', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mbti_indicators', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('big5_traits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('predicted_mbti', sa.String(length=4), nullable=True),
        sa.Column('keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('topics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('entities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('themes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('lifestyle_patterns', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('activity_patterns', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('social_patterns', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('insights', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('recommendations', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('analysis_version', sa.String(length=50), nullable=True),
        sa.Column('processing_time_seconds', sa.Float(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('processed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_diary_analysis_analysis_id'), 'diary_analysis', ['analysis_id'], unique=True)
    op.create_index(op.f('ix_diary_analysis_diary_id'), 'diary_analysis', ['diary_id'], unique=False)
    op.create_index(op.f('ix_diary_analysis_id'), 'diary_analysis', ['id'], unique=False)
    op.create_index(op.f('ix_diary_analysis_user_id'), 'diary_analysis', ['user_id'], unique=False)

    # 사용자 벡터 테이블 생성
    op.create_table('user_vectors',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('personality_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('emotion_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('lifestyle_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('combined_vector', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('vector_version', sa.String(length=20), nullable=True),
        sa.Column('analysis_count', sa.Integer(), nullable=True),
        sa.Column('confidence_score', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_vectors_user_id'), 'user_vectors', ['user_id'], unique=False)

    # 사용자 성격 요약 테이블 생성
    op.create_table('user_personality_summary',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('overall_mbti', sa.String(length=4), nullable=True),
        sa.Column('overall_big5', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('personality_traits', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mbti_consistency', sa.Float(), nullable=True),
        sa.Column('trait_stability', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('personality_evolution', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('analysis_count', sa.Integer(), nullable=True),
        sa.Column('confidence_level', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_personality_summary_user_id'), 'user_personality_summary', ['user_id'], unique=False)

    # 사용자 감정 패턴 테이블 생성
    op.create_table('user_emotion_patterns',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('emotion_distribution', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('dominant_emotions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('avg_sentiment_score', sa.Float(), nullable=True),
        sa.Column('emotional_range', sa.Float(), nullable=True),
        sa.Column('emotional_volatility', sa.Float(), nullable=True),
        sa.Column('weekly_pattern', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('monthly_pattern', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('seasonal_pattern', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('emotion_trends', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('sentiment_trends', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('analysis_count', sa.Integer(), nullable=True),
        sa.Column('analysis_period_days', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_emotion_patterns_user_id'), 'user_emotion_patterns', ['user_id'], unique=False)

    # 매칭 선호도 테이블 생성
    op.create_table('matching_preferences',
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=True),
        sa.Column('visibility', sa.String(length=20), nullable=True),
        sa.Column('preferred_age_min', sa.Integer(), nullable=True),
        sa.Column('preferred_age_max', sa.Integer(), nullable=True),
        sa.Column('preferred_location_radius', sa.Integer(), nullable=True),
        sa.Column('preferred_personality_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('personality_weight', sa.Integer(), nullable=True),
        sa.Column('emotion_weight', sa.Integer(), nullable=True),
        sa.Column('lifestyle_weight', sa.Integer(), nullable=True),
        sa.Column('interest_weight', sa.Integer(), nullable=True),
        sa.Column('min_compatibility_threshold', sa.Integer(), nullable=True),
        sa.Column('diversity_factor', sa.Integer(), nullable=True),
        sa.Column('excluded_users', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('blocked_users', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_matching_preferences_user_id'), 'matching_preferences', ['user_id'], unique=False)

    # AI 모델 버전 테이블 생성
    op.create_table('ai_model_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('model_type', sa.String(length=50), nullable=False),
        sa.Column('model_config', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('api_endpoint', sa.String(length=255), nullable=True),
        sa.Column('performance_metrics', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('accuracy_score', sa.Float(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_default', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('deployed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """다운그레이드 마이그레이션"""
    op.drop_table('ai_model_versions')
    op.drop_index(op.f('ix_matching_preferences_user_id'), table_name='matching_preferences')
    op.drop_table('matching_preferences')
    op.drop_index(op.f('ix_user_emotion_patterns_user_id'), table_name='user_emotion_patterns')
    op.drop_table('user_emotion_patterns')
    op.drop_index(op.f('ix_user_personality_summary_user_id'), table_name='user_personality_summary')
    op.drop_table('user_personality_summary')
    op.drop_index(op.f('ix_user_vectors_user_id'), table_name='user_vectors')
    op.drop_table('user_vectors')
    op.drop_index(op.f('ix_diary_analysis_user_id'), table_name='diary_analysis')
    op.drop_index(op.f('ix_diary_analysis_id'), table_name='diary_analysis')
    op.drop_index(op.f('ix_diary_analysis_diary_id'), table_name='diary_analysis')
    op.drop_index(op.f('ix_diary_analysis_analysis_id'), table_name='diary_analysis')
    op.drop_table('diary_analysis')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_firebase_uid'), table_name='users')
    op.drop_table('users')
