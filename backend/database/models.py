import datetime
from typing import List, Optional
from sqlalchemy import (
    Integer, String, Text, DateTime, ForeignKey, 
    Boolean, Float, JSON, Index, func, UniqueConstraint
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Source(Base):
    """Data sources for research papers (e.g. arXiv, OpenAlex)."""
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    base_url: Mapped[str] = mapped_column(String(255), nullable=False)
    rate_limit_per_minute: Mapped[int] = mapped_column(Integer, default=60)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    papers: Mapped[List["Paper"]] = relationship("Paper", back_populates="source_rel")
    ingestion_jobs: Mapped[List["IngestionJob"]] = relationship("IngestionJob", back_populates="source_rel")


class Author(Base):
    """Author entities with affiliations."""
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    author_id: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    affiliation: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    orcid: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    paper_associations: Mapped[List["PaperAuthor"]] = relationship("PaperAuthor", back_populates="author", cascade="all, delete-orphan")


class PaperAuthor(Base):
    """Junction table linking papers and authors with ordering."""
    __tablename__ = "paper_authors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id: Mapped[int] = mapped_column(Integer, ForeignKey("authors.id", ondelete="CASCADE"), nullable=False, index=True)
    author_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_corresponding: Mapped[bool] = mapped_column(Boolean, default=False)

    paper: Mapped["Paper"] = relationship("Paper", back_populates="author_associations")
    author: Mapped["Author"] = relationship("Author", back_populates="paper_associations")

    __table_args__ = (
        UniqueConstraint("paper_id", "author_id", name="uq_paper_author"),
    )


class Paper(Base):
    """Canonical research paper records."""
    __tablename__ = "papers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="arxiv", index=True)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    primary_category: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    storage_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    source_rel: Mapped[Optional["Source"]] = relationship("Source", back_populates="papers")
    author_associations: Mapped[List["PaperAuthor"]] = relationship("PaperAuthor", back_populates="paper", cascade="all, delete-orphan", order_by="PaperAuthor.author_order")
    versions: Mapped[List["PaperVersion"]] = relationship("PaperVersion", back_populates="paper", cascade="all, delete-orphan", order_by="PaperVersion.version_number")
    processing_jobs: Mapped[List["ProcessingJob"]] = relationship("ProcessingJob", back_populates="paper_rel")

    __table_args__ = (
        Index("ix_papers_published_at_desc", published_at.desc()),
    )


class PaperVersion(Base):
    """Tracks revisions for a paper (e.g. arXiv v1, v2, v3)."""
    __tablename__ = "paper_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    paper_id: Mapped[int] = mapped_column(Integer, ForeignKey("papers.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    diff_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    storage_path: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    published_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    paper: Mapped["Paper"] = relationship("Paper", back_populates="versions")

    __table_args__ = (
        UniqueConstraint("paper_id", "version_number", name="uq_paper_version"),
    )


class IngestionJob(Base):
    """Job queue records for paper harvesting/ingestion."""
    __tablename__ = "ingestion_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    source_name: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sources.id", ondelete="SET NULL"), nullable=True)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    source_rel: Mapped[Optional["Source"]] = relationship("Source", back_populates="ingestion_jobs")


class ProcessingJob(Base):
    """Tracks background processing (PDF extraction, embedding, summarization)."""
    __tablename__ = "processing_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    paper_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    paper_internal_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("papers.id", ondelete="SET NULL"), nullable=True)
    job_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_retries: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    idempotency_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    result: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    paper_rel: Mapped[Optional["Paper"]] = relationship("Paper", back_populates="processing_jobs")
