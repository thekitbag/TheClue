"""Player model

Revision ID: 2fa56b371687
Revises: 33c055757140
Create Date: 2024-12-07 17:11:21.675823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2fa56b371687'
down_revision = '33c055757140'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('quiz_id', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['quiz_id'], ['quiz.quiz_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('player', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_player_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_player_quiz_id'), ['quiz_id'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('player', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_player_quiz_id'))
        batch_op.drop_index(batch_op.f('ix_player_name'))

    op.drop_table('player')
    # ### end Alembic commands ###
