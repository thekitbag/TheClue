"""answer model

Revision ID: 5584bbaad666
Revises: b0097570da66
Create Date: 2024-12-21 06:50:10.289569

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5584bbaad666'
down_revision = 'b0097570da66'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('answer',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('answer_text', sa.String(length=255), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['player.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['question.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_answer_player_id'), ['player_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_answer_question_id'), ['question_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('answer', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_answer_question_id'))
        batch_op.drop_index(batch_op.f('ix_answer_player_id'))

    op.drop_table('answer')
    # ### end Alembic commands ###