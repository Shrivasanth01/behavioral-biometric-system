import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.database import Base, engine, async_session_factory
from app.models.user import User, UserRole, UserStatus
from app.models.account import Account, AccountType, AccountStatus
from app.services.auth_service import hash_password
from sqlalchemy import select

async def seed_data():
    async with async_session_factory() as db:
        print("[+] Creating database schema if not exists...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        print("[+] Seeding demo users...")
        users_data = [
            {
                "email": "admin@bbs.com",
                "phone": "+15550000001",
                "password_hash": hash_password("Admin@123456"),
                "full_name": "System Administrator",
                "role": UserRole.ADMIN,
                "status": UserStatus.ACTIVE
            },
            {
                "email": "analyst@bbs.com",
                "phone": "+15550000002",
                "password_hash": hash_password("Analyst@123456"),
                "full_name": "Security Analyst",
                "role": UserRole.ANALYST,
                "status": UserStatus.ACTIVE
            },
            {
                "email": "user@bbs.com",
                "phone": "+15550000003",
                "password_hash": hash_password("User@123456"),
                "full_name": "John Doe",
                "role": UserRole.CUSTOMER,
                "status": UserStatus.ACTIVE
            },
            {
                "email": "shrivasanth123@gmail.com",
                "phone": "+15550000004",
                "password_hash": hash_password("User@123456"),
                "full_name": "Shrivasanth Customer",
                "role": UserRole.CUSTOMER,
                "status": UserStatus.ACTIVE
            }
        ]

        created_users = {}
        for u_data in users_data:
            res = await db.execute(select(User).where(User.email == u_data["email"]))
            existing = res.scalar_one_or_none()
            if not existing:
                u = User(**u_data)
                db.add(u)
                await db.flush()
                await db.refresh(u)
                created_users[u.email] = u
                print(f"    - Created user: {u.email} ({u.role.value})")
            else:
                existing.password_hash = u_data["password_hash"]
                created_users[existing.email] = existing
                print(f"    - User already exists: {existing.email} ({existing.role.value})")

        for email, user in created_users.items():
            if user.role == UserRole.CUSTOMER:
                print(f"[+] Seeding accounts for {user.email}...")
                acc_res = await db.execute(select(Account).where(Account.user_id == user.id))
                accs = acc_res.scalars().all()
                if not accs:
                    acc1 = Account(
                        user_id=user.id,
                        account_number=f"1000{user.id}920192",
                        account_type=AccountType.SAVINGS,
                        currency="USD",
                        balance=25000.50,
                        status=AccountStatus.ACTIVE
                    )
                    acc2 = Account(
                        user_id=user.id,
                        account_number=f"2000{user.id}920193",
                        account_type=AccountType.CHECKING,
                        currency="USD",
                        balance=8450.00,
                        status=AccountStatus.ACTIVE
                    )
                    db.add_all([acc1, acc2])
                    await db.flush()
                    print(f"    - Created Savings & Checking accounts for user {user.id}.")

        await db.commit()
        print("[+] Seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
