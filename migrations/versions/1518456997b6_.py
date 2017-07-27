"""empty message

Revision ID: 1518456997b6
Revises: 
Create Date: 2017-07-20 13:44:59.483890

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1518456997b6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('employees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(length=45), nullable=False),
    sa.Column('last_name', sa.String(length=45), nullable=True),
    sa.Column('reporting_manager', sa.Integer(), nullable=True),
    sa.Column('designation', sa.String(length=45), nullable=False),
    sa.Column('department', sa.String(length=45), nullable=False),
    sa.Column('total_leaves_allowed', sa.Integer(), nullable=False),
    sa.Column('leaves_availed', sa.Integer(), nullable=False),
    sa.Column('leaves_remaining', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('balance_sheet',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('emp_id', sa.Integer(), nullable=False),
    sa.Column('from_date', sa.DateTime(), nullable=False),
    sa.Column('to_date', sa.DateTime(), nullable=False),
    sa.Column('leave_type', sa.Enum('General', 'Medical'), nullable=False),
    sa.Column('purpose', sa.String(length=200), nullable=False),
    sa.Column('pay', sa.Enum('Payed', 'Unpayed'), nullable=False),
    sa.Column('hr_remark', sa.String(length=128), nullable=True),
    sa.Column('manager_remark', sa.String(length=128), nullable=True),
    sa.Column('hr_approval', sa.Integer(), nullable=False),
    sa.Column('manager_approval', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['emp_id'], ['employees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('balance_sheet')
    op.drop_table('employees')
    op.drop_table('user')
    # ### end Alembic commands ###
