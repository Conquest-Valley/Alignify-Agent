# Live Run Step 2 Registry Package

This package turns the Google Sheet workbook into a normalized client payload and a Stage 2 compatible live registry JSON file.

It does not fetch Google Docs, Basecamp, GA4, or GSC content yet.
It does:
- validate the workbook shape
- normalize one real client row
- normalize Source Index rows
- normalize Producer Notes rows
- create a client memory stub
- create a Stage 2 compatible live registry file
- create output artifacts for the next connector steps
