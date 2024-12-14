from __init__ import CURSOR, CONN
from department import Department
from employee import Employee


class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employees(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """Save the review instance to the database"""
        if self.id is None:  # New instance
            CURSOR.execute(
                """
                INSERT INTO reviews (year, summary, employee_id) 
                VALUES (?, ?, ?)
                """,
                (self.year, self.summary, self.employee_id),
            )
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        else:  # Update existing instance
            self.update()

    @classmethod
    def create(cls, year, summary, employee_id):
        """Create a new Review instance and persist it"""
        review = cls(year=year, summary=summary, employee_id=employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """Create or retrieve a Review instance from the database row"""
        review_id, year, summary, employee_id = row
        if review_id in cls.all:
            # Return existing instance from memory if already cached
            return cls.all[review_id]
        # Create a new Review instance and cache it
        review = cls(id=review_id, year=year, summary=summary, employee_id=employee_id)
        cls.all[review_id] = review
        return review

    @classmethod
    def find_by_id(cls, review_id):
        """Find a review instance by its ID"""
        CURSOR.execute("SELECT * FROM reviews WHERE id = ?", (review_id,))
        row = CURSOR.fetchone()
        return cls.instance_from_db(row) if row else None

    def update(self):
        """Update the corresponding database record with instance values"""
        CURSOR.execute(
            """
            UPDATE reviews
            SET year = ?, summary = ?, employee_id = ?
            WHERE id = ?
            """,
            (self.year, self.summary, self.employee_id, self.id),
        )
        CONN.commit()

    def delete(self):
        """Delete the instance from the database and memory"""
        CURSOR.execute("DELETE FROM reviews WHERE id = ?", (self.id,))
        Review.all.pop(self.id, None)
        self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        """Retrieve all reviews as instances"""
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if isinstance(value, int) and value >= 2000:
            self._year = value
        else:
            raise ValueError("Year must be an integer greater than or equal to 2000")

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if isinstance(value, str) and value.strip():
            self._summary = value
        else:
            raise ValueError("Summary must be a non-empty string")

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        # Ensure the employee exists in the database
        CURSOR.execute("SELECT id FROM employees WHERE id = ?", (value,))
        if CURSOR.fetchone():
            self._employee_id = value
        else:
            raise ValueError(
                "Employee ID must match an existing employee in the database"
            )
