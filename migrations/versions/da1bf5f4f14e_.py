"""empty message

Revision ID: da1bf5f4f14e
Revises: 
Create Date: 2018-05-06 18:53:20.580099

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'da1bf5f4f14e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('finances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('salary', sa.Integer(), nullable=True),
    sa.Column('occupation', sa.String(length=64), nullable=True),
    sa.Column('employer', sa.String(length=64), nullable=True),
    sa.Column('time_employed', sa.Integer(), nullable=True),
    sa.Column('employment_status', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_default'), 'roles', ['default'], unique=False)
    op.create_table('terms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('installments', sa.Integer(), nullable=True),
    sa.Column('rate', sa.DECIMAL(precision=2), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('firstname', sa.String(length=64), nullable=True),
    sa.Column('lastname', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('cpf', sa.Integer(), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('address',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('street', sa.String(length=64), nullable=True),
    sa.Column('house', sa.Integer(), nullable=True),
    sa.Column('apartment', sa.String(length=16), nullable=True),
    sa.Column('city', sa.String(length=64), nullable=True),
    sa.Column('state', sa.String(length=64), nullable=True),
    sa.Column('country', sa.String(length=64), nullable=True),
    sa.Column('zipcode', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('connection',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('borrower_id', sa.Integer(), nullable=True),
    sa.Column('guarantor_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=64), nullable=True),
    sa.Column('amount', sa.Numeric(), nullable=True),
    sa.Column('message', sa.String(length=256), nullable=True),
    sa.Column('last_update', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['borrower_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['guarantor_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('application',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Numeric(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.Column('submitted_at', sa.DateTime(), nullable=True),
    sa.Column('decision_at', sa.DateTime(), nullable=True),
    sa.Column('processed_by_id', sa.Integer(), nullable=True),
    sa.Column('approved_by_id', sa.Integer(), nullable=True),
    sa.Column('borrower_id', sa.Integer(), nullable=True),
    sa.Column('guarantor_id', sa.Integer(), nullable=True),
    sa.Column('connection_id', sa.Integer(), nullable=True),
    sa.Column('terms_id', sa.Integer(), nullable=True),
    sa.Column('message', sa.String(length=256), nullable=True),
    sa.Column('borrower_address_id', sa.Integer(), nullable=True),
    sa.Column('guarantor_address_id', sa.Integer(), nullable=True),
    sa.Column('borrower_finances_id', sa.Integer(), nullable=True),
    sa.Column('guarantor_finances_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['approved_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['borrower_address_id'], ['address.id'], ),
    sa.ForeignKeyConstraint(['borrower_finances_id'], ['finances.id'], ),
    sa.ForeignKeyConstraint(['borrower_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['connection_id'], ['connection.id'], ),
    sa.ForeignKeyConstraint(['guarantor_address_id'], ['address.id'], ),
    sa.ForeignKeyConstraint(['guarantor_finances_id'], ['finances.id'], ),
    sa.ForeignKeyConstraint(['guarantor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['processed_by_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['terms_id'], ['terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('loan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('application_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=64), nullable=True),
    sa.Column('missed_payments', sa.Integer(), nullable=True),
    sa.Column('principal', sa.Numeric(), nullable=True),
    sa.Column('outstanding', sa.Numeric(), nullable=True),
    sa.Column('terms_id', sa.Integer(), nullable=True),
    sa.Column('loan_date', sa.DateTime(), nullable=True),
    sa.Column('borrower_id', sa.Integer(), nullable=True),
    sa.Column('guarantor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['application_id'], ['application.id'], ),
    sa.ForeignKeyConstraint(['borrower_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['guarantor_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['terms_id'], ['terms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('loan_id', sa.Integer(), nullable=True),
    sa.Column('payment', sa.Numeric(), nullable=True),
    sa.Column('penalty', sa.Integer(), nullable=True),
    sa.Column('scheduled_date', sa.DateTime(), nullable=True),
    sa.Column('payment_date', sa.DateTime(), nullable=True),
    sa.Column('paid', sa.Integer(), nullable=True),
    sa.Column('paid_by_borrower', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['loan_id'], ['loan.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payments')
    op.drop_table('loan')
    op.drop_table('application')
    op.drop_table('connection')
    op.drop_table('address')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('terms')
    op.drop_index(op.f('ix_roles_default'), table_name='roles')
    op.drop_table('roles')
    op.drop_table('finances')
    # ### end Alembic commands ###
