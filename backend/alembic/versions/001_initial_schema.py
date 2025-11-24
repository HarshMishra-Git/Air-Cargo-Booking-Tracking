"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2025-11-23 07:22:57.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create flights table
    op.create_table(
        'flights',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('flight_number', sa.String(length=20), nullable=False),
        sa.Column('airline_name', sa.String(length=100), nullable=False),
        sa.Column('departure_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('arrival_datetime', sa.DateTime(timezone=True), nullable=False),
        sa.Column('origin', sa.String(length=10), nullable=False),
        sa.Column('destination', sa.String(length=10), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create bookings table
    op.create_table(
        'bookings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ref_id', sa.String(length=20), nullable=False),
        sa.Column('origin', sa.String(length=10), nullable=False),
        sa.Column('destination', sa.String(length=10), nullable=False),
        sa.Column('pieces', sa.Integer(), nullable=False),
        sa.Column('weight_kg', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='BOOKED'),
        sa.Column('flight_ids', postgresql.ARRAY(sa.Integer()), server_default='{}', nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint("status IN ('BOOKED', 'DEPARTED', 'ARRIVED', 'DELIVERED', 'CANCELLED')", name='chk_status'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ref_id')
    )
    
    # Create booking_events table
    op.create_table(
        'booking_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('booking_id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=20), nullable=False),
        sa.Column('location', sa.String(length=10), nullable=True),
        sa.Column('flight_id', sa.Integer(), nullable=True),
        sa.Column('flight_number', sa.String(length=20), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.CheckConstraint("event_type IN ('BOOKED', 'DEPARTED', 'ARRIVED', 'DELIVERED', 'CANCELLED')", name='chk_event_type'),
        sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['flight_id'], ['flights.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_bookings_ref_id', 'bookings', ['ref_id'])
    op.create_index('idx_bookings_status', 'bookings', ['status'])
    op.create_index('idx_bookings_created_at', 'bookings', [sa.text('created_at DESC')])
    op.create_index('idx_flights_route_date', 'flights', ['origin', 'destination', 'departure_datetime'])
    op.create_index('idx_flights_origin', 'flights', ['origin'])
    op.create_index('idx_flights_destination', 'flights', ['destination'])
    op.create_index('idx_flights_departure', 'flights', ['departure_datetime'])
    op.create_index('idx_booking_events_booking_id', 'booking_events', ['booking_id', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_booking_events_booking_id', table_name='booking_events')
    op.drop_index('idx_flights_departure', table_name='flights')
    op.drop_index('idx_flights_destination', table_name='flights')
    op.drop_index('idx_flights_origin', table_name='flights')
    op.drop_index('idx_flights_route_date', table_name='flights')
    op.drop_index('idx_bookings_created_at', table_name='bookings')
    op.drop_index('idx_bookings_status', table_name='bookings')
    op.drop_index('idx_bookings_ref_id', table_name='bookings')
    op.drop_table('booking_events')
    op.drop_table('bookings')
    op.drop_table('flights')