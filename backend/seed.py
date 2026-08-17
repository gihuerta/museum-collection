"""Populate the database with sample catalog items for local development/demo.

Run with: python seed.py
"""
from app import create_app
from models import db, Item

SAMPLE_ITEMS = [
    dict(title="Frida Kahlo: The Paintings", category="book", creator="Hayden Herrera",
         donor="Estate of M. Alvarez", accession_number="BK-0001", condition="good",
         location="Shelf A3", description="Illustrated survey of Kahlo's major works.",
         tags="art,mexican art,painting"),
    dict(title="Diego Rivera: A Retrospective", category="book", creator="Cynthia Newman Helms",
         donor="University Press Donation", accession_number="BK-0002", condition="excellent",
         location="Shelf A3", description="Catalog from the 1986 Detroit Institute of Arts retrospective.",
         tags="art,mexican art,muralism"),
    dict(title="The Muralist Movement in Mexico", category="book", creator="Desmond Rochfort",
         donor="Estate of M. Alvarez", accession_number="BK-0003", condition="fair",
         location="Shelf A4", description="History of the Mexican muralism movement, 1920s-1950s.",
         tags="art,muralism,history"),
    dict(title="Voces del Barrio: Oral Histories", category="book", creator="Community Oral History Project",
         donor="Pilsen Neighborhood Association", accession_number="BK-0004", condition="good",
         location="Shelf B1", description="Collected oral histories from Chicago's Pilsen neighborhood.",
         tags="oral history,community,chicago"),

    dict(title="Chicago Tribune, Dia de los Muertos coverage", category="archive",
         creator=None, donor="Chicago Public Library", accession_number="AR-0142",
         condition="fair", location="Box 12", description="Newspaper clippings, 1998-2003.",
         tags="newspaper,dia de los muertos,chicago"),
    dict(title="Pilsen Neighborhood Newsletter Collection", category="archive",
         creator=None, donor="Pilsen Neighborhood Association", accession_number="AR-0143",
         condition="poor", location="Box 12", description="Community newsletters, 1985-1995, some water damage.",
         tags="newsletter,pilsen,community"),
    dict(title="1968 Chicano Moratorium flyers", category="archive", creator=None,
         donor="Anonymous", accession_number="AR-0144", condition="fair", location="Box 14",
         description="Original protest flyers and pamphlets from the anti-war movement.",
         tags="activism,chicano movement,protest"),
    dict(title="Museum founding correspondence", category="archive", creator="Founding Board",
         donor="Museum Archives", accession_number="AR-0145", condition="good", location="Box 1",
         description="Letters and meeting minutes from the museum's founding in 1982.",
         tags="institutional history,correspondence"),

    dict(title="Untitled mural study", category="artifact", creator="Unknown",
         donor="Anonymous", accession_number="AF-0007", condition="poor",
         location="Storage Vault 2", description="Sketch on canvas, water damage on lower edge.",
         tags="mural,study,sketch"),
    dict(title="Day of the Dead altar (ofrenda) sculpture", category="artifact",
         creator="Maria Elena Torres", donor="Torres Family", accession_number="AF-0008",
         condition="excellent", location="Storage Vault 1",
         description="Mixed-media ofrenda sculpture with papel picado and marigolds, 2005.",
         tags="dia de los muertos,sculpture,folk art"),
    dict(title="Traditional Oaxacan textile loom", category="artifact", creator="Unknown Artisan",
         donor="Oaxaca Cultural Exchange", accession_number="AF-0009", condition="good",
         location="Storage Vault 3", description="Backstrap loom used for traditional weaving demonstrations.",
         tags="textile,oaxaca,craft"),
    dict(title="Ceramic calavera figurine set", category="artifact", creator="Jose Ramirez",
         donor="Ramirez Family", accession_number="AF-0010", condition="good",
         location="Storage Vault 1", description="Set of six hand-painted ceramic skull figurines.",
         tags="dia de los muertos,ceramic,folk art"),

    dict(title="Portrait of a Textile Worker", category="photo", creator="R. Ibarra",
         donor="Ibarra Family", accession_number="PH-0056", condition="excellent",
         location="Flat File 4", description="Silver gelatin print, 1974.",
         tags="photography,labor,portrait"),
    dict(title="Pilsen mural documentation series", category="photo", creator="Museum Staff",
         donor="Museum Archives", accession_number="PH-0057", condition="excellent",
         location="Flat File 4", description="Color photographs documenting neighborhood murals, 2010-2012.",
         tags="photography,mural,pilsen"),
    dict(title="1970 Chicano Moratorium march", category="photo", creator="Unknown Photographer",
         donor="Anonymous", accession_number="PH-0058", condition="fair",
         location="Flat File 5", description="Black and white print of a protest march in downtown Chicago.",
         tags="photography,activism,chicano movement"),
    dict(title="Quinceañera portrait, 1985", category="photo", creator="Studio Reyes",
         donor="Reyes Family", accession_number="PH-0059", condition="good",
         location="Flat File 5", description="Color studio portrait, part of a donated family collection.",
         tags="photography,family,tradition"),

    dict(title="Community programming binder", category="other", creator="Education Department",
         donor="Museum Archives", accession_number="OT-0001", condition="good",
         location="Office Storage", description="Reference binder of past workshops and school tour scripts.",
         tags="education,programming"),
]

# ---------------------------------------------------------------------------
# Intentionally flawed records for exercising GET /api/items/validate.
# These bypass the API's own validation (which would normally reject them)
# by writing straight to the DB, the same way bad legacy data or a messy
# CSV import might end up in a real catalog.
# ---------------------------------------------------------------------------
BAD_TEST_ITEMS = [
    # Issue: missing accession number
    dict(title="Unlabeled photograph, donor unknown", category="photo", creator=None,
         donor="Anonymous", accession_number=None, condition="fair",
         location="Flat File 6", description="Found in a donated box, no accompanying documentation.",
         tags="photography,unidentified"),

    # Issue: unrecognized/invalid category (not in VALID_CATEGORIES)
    dict(title="Hand-carved wooden mask", category="sculpture", creator="Unknown",
         donor="Anonymous", accession_number="AF-0099", condition="good",
         location="Storage Vault 2", description="Miscategorized during a rushed intake — needs review.",
         tags="mask,folk art"),

    # Issue: missing title
    dict(title="", category="archive", creator=None, donor="Estate Donation",
         accession_number="AR-0199", condition="poor", location="Box 20",
         description="Box of unsorted papers, never cataloged properly.",
         tags="uncataloged"),

    # Issue: duplicate accession number (matches BK-0001 above)
    dict(title="Frida Kahlo: The Paintings (duplicate entry)", category="book",
         creator="Hayden Herrera", donor="Unknown", accession_number="BK-0001",
         condition="fair", location="Shelf A3",
         description="Accidental double-entry from a prior inventory pass.",
         tags="art,duplicate"),

    # Issue: another duplicate accession number (matches PH-0056 above)
    dict(title="Portrait of a Textile Worker (re-scanned copy)", category="photo",
         creator="R. Ibarra", donor="Ibarra Family", accession_number="PH-0056",
         condition="good", location="Flat File 4",
         description="Second print of the same photo, logged under the same number by mistake.",
         tags="photography,duplicate"),
]


def run(include_bad_data=True, reset=False):
    app = create_app()
    with app.app_context():
        if reset:
            deleted = Item.query.delete()
            db.session.commit()
            print(f"Cleared {deleted} existing item(s).")
        elif Item.query.count() > 0:
            print("Database already has items — skipping seed. Use --reset to reseed from scratch.")
            return

        for data in SAMPLE_ITEMS:
            db.session.add(Item(**data))

        if include_bad_data:
            for data in BAD_TEST_ITEMS:
                db.session.add(Item(**data))

        db.session.commit()

        print(f"Seeded {len(SAMPLE_ITEMS)} clean items.")
        if include_bad_data:
            print(f"Seeded {len(BAD_TEST_ITEMS)} intentionally flawed items for testing /api/items/validate:")
            print("  - 1 missing accession number")
            print("  - 1 unrecognized category ('sculpture')")
            print("  - 1 missing title")
            print("  - 2 duplicate accession numbers (BK-0001, PH-0056)")


if __name__ == "__main__":
    import sys
    run(
        include_bad_data="--clean" not in sys.argv,
        reset="--reset" in sys.argv,
    )
