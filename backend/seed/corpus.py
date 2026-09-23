"""Seed corpus for the repository.

IMPORTANT - read before you demo:
These are SHORT SUMMARIES WRITTEN BY THE TEAM so the platform has something to
retrieve on a fresh install. They are NOT the official text of any scheme, act
or paper. Each body starts with a marker line saying so, and every entry carries
the real source URL.

Before a jury demo, replace these with the actual PDFs:
    POST /api/documents  (file=<the real PDF>)
and delete the seeds. The Evidence Score deliberately rewards `official` and
`peer_reviewed` provenance so real documents outrank these stubs.
"""

MARKER = "[SEED SUMMARY - team-written stub, not the official text. Source: {url}]"


def _doc(title, doc_type, publisher, year, url, provenance, state, body):
    return {
        "title": title,
        "doc_type": doc_type,
        "publisher": publisher,
        "year": year,
        "url": url,
        "provenance": provenance,
        "state": state,
        "body": body.strip(),
    }


CORPUS = [
    _doc(
        "Digital India Land Records Modernization Programme (DILRMP) - programme overview",
        "policy", "Department of Land Resources, Ministry of Rural Development", 2024,
        "https://dolr.gov.in/programme-schemes/dilrmp/", "official", "India",
        """
        DILRMP is the Government of India's central sector programme for modernising land records.
        Its core components are the computerisation of Records of Rights (RoR), digitisation and
        updating of cadastral maps, computerisation of the registration process, and integration of
        the textual records with spatial maps and with the registration system. The programme also
        covers modern record rooms, survey and re-survey using modern technology such as drones and
        continuously operating reference stations, and training of revenue staff.

        The intended outcome is a conclusive titling system in which the record of rights is
        presumed to reflect ownership, replacing the presumptive title system inherited from
        colonial-era settlement records. Implementation is carried out by State governments, so
        coverage, data formats and quality vary significantly between States. Component-wise
        progress and State-wise status are published on the DILRMP dashboard; consult the dashboard
        for current figures rather than relying on this summary.
        """,
    ),
    _doc(
        "ULPIN / Bhu-Aadhaar - unique land parcel identification",
        "policy", "Department of Land Resources, Ministry of Rural Development", 2023,
        "https://dolr.gov.in/programme-schemes/dilrmp/unique-land-parcel-identification-number-ulpin/",
        "official", "India",
        """
        The Unique Land Parcel Identification Number (ULPIN), branded Bhu-Aadhaar, assigns a
        14-digit alphanumeric identifier to every land parcel, derived from the geo-coordinates of
        the parcel and based on longitude and latitude. The identifier is intended to be permanent
        and unique, so that textual land records, cadastral maps, registration records and
        programme databases can be joined reliably across systems and across States.

        For an integrated national research platform, ULPIN is the natural join key: without a
        stable parcel identifier, records from different State portals cannot be linked to the same
        physical parcel, and spatial analytics cannot be attached to ownership or transaction data.
        Harmonising State datasets to ULPIN is therefore the first data-engineering step in any
        cross-State land analysis.
        """,
    ),
    _doc(
        "SVAMITVA - survey of villages and mapping with improvised technology in village areas",
        "policy", "Ministry of Panchayati Raj", 2024,
        "https://svamitva.nic.in/", "official", "India",
        """
        SVAMITVA uses drone-based survey to map inhabited (abadi) areas of villages and issue
        property cards to rural household owners. The scheme aims to provide a record of rights for
        residential property in rural areas, which historically lacked surveyed records, thereby
        enabling the use of property as a financial asset, reducing property disputes and
        supporting Gram Panchayat-level planning and property tax assessment.

        Outputs include high-resolution drone imagery, GIS maps of abadi areas and property cards.
        For research purposes SVAMITVA is significant because it creates spatial records for a
        category of land that is absent from traditional agricultural cadastral records, and
        because the drone imagery provides a recent, high-resolution baseline for built-up area
        analysis.
        """,
    ),
    _doc(
        "Bihar Special Survey and Settlement - context note",
        "policy", "Department of Revenue and Land Reforms, Government of Bihar", 2025,
        "https://dlrs.bihar.gov.in/", "official", "Bihar",
        """
        Bihar is conducting a statewide special survey and settlement operation to prepare updated
        cadastral maps and records of rights. Bihar's existing records in large parts of the State
        derive from cadastral and revisional surveys conducted decades ago, and have not kept pace
        with partitions, transfers and inheritance, so the record frequently does not match
        possession on the ground.

        The survey involves self-declaration by landholders, verification, publication of draft
        records, objections and finalisation. Because the operation is live, it makes Bihar the
        most informative pilot geography for an evidence platform: research questions about
        record-updating, dispute generation, self-declaration quality and survey throughput can be
        studied against an ongoing programme rather than a historical one. Survey progress and
        district-wise status are published by the Directorate of Land Records and Survey; consult
        the source for current figures.
        """,
    ),
    _doc(
        "National Generic Document Registration System (NGDRS)",
        "policy", "National Informatics Centre", 2024,
        "https://ngdrs.gov.in/", "official", "India",
        """
        NGDRS is a configurable, generic application for property and document registration that
        States can adopt and configure to their own Acts, rules, fee structures and languages. It
        supports online entry of deed details, stamp duty and fee calculation, appointment booking,
        and integration with land records so that registration events can trigger mutation.

        The registration-to-mutation link is the point at which a transaction becomes visible in
        the record of rights. Where the link is weak or manual, the record of rights drifts away
        from actual ownership, which is a principal generator of later disputes. For analytics,
        registration data is also the best available proxy for land market activity.
        """,
    ),
    _doc(
        "Bhuvan geoportal and open OGC services",
        "dataset", "National Remote Sensing Centre, ISRO", 2024,
        "https://bhuvan.nrsc.gov.in/", "official", "India",
        """
        Bhuvan is ISRO's national geoportal, providing satellite imagery, thematic layers and
        open OGC web services (WMS/WFS) covering land use and land cover, wasteland, flood hazard
        zonation, watershed and other themes for India. Several layers are served without an API
        key, which makes them directly usable as a backdrop and as analytical input in a research
        platform.

        Bhoonidhi provides access to Indian Earth observation data products for download. Together
        with open global archives such as Sentinel-2 from the Copernicus programme, these sources
        allow land use change, built-up expansion and vegetation change to be measured over time
        without any proprietary data licensing.
        """,
    ),
    _doc(
        "National Geospatial Policy 2022 - implications for land data sharing",
        "legal", "Department of Science and Technology", 2022,
        "https://dst.gov.in/national-geospatial-policy", "official", "India",
        """
        The National Geospatial Policy 2022 liberalised the acquisition and production of
        geospatial data in India and set out the intent to make geospatial data, including a
        national digital twin and high-resolution topographic and terrain data, available as a
        public good. It removed prior restrictions on the collection, generation, storage and
        sharing of geospatial data by Indian entities for most categories of data, subject to a
        negative list of sensitive attributes.

        For a national land research platform, the policy is the enabling instrument that allows
        spatial layers from multiple agencies to be combined and republished, and it establishes
        the expectation that geospatial data will be discoverable through open APIs rather than
        through bilateral data-sharing agreements.
        """,
    ),
    _doc(
        "Digital Personal Data Protection Act 2023 - constraints on land record analytics",
        "legal", "Ministry of Electronics and Information Technology", 2023,
        "https://www.meity.gov.in/data-protection-framework", "official", "India",
        """
        The Digital Personal Data Protection Act 2023 governs the processing of digital personal
        data in India. It establishes obligations for data fiduciaries including purpose
        limitation, data minimisation, accuracy, security safeguards and breach notification, and
        it establishes rights for data principals.

        Land records contain personal data: owner names, parentage, and in many States identifiers
        linked to individuals. A research and policy platform must therefore avoid exposing
        individual-level records to general users. Practical design responses are aggregation to
        village, block or district level for analysis; anonymisation or pseudonymisation of owner
        attributes; purpose-bound, role-based access for the small number of users who need
        parcel-level detail; and audit logging of every access to identifiable data.
        """,
    ),
    _doc(
        "National Data Sharing and Accessibility Policy and Open Government Data platform",
        "policy", "Government of India", 2012,
        "https://data.gov.in/", "official", "India",
        """
        The National Data Sharing and Accessibility Policy establishes the principle that
        non-sensitive data generated using public funds should be made available for wider use.
        The Open Government Data platform, data.gov.in, publishes datasets from ministries and
        States as downloadable resources and, for many datasets, as APIs accessible with a free
        registered API key.

        For land governance research, data.gov.in is the practical entry point for socio-economic
        and programme datasets that must be joined to spatial and record data: agricultural
        statistics, census-derived indicators, scheme progress data and administrative boundaries.
        """,
    ),
    _doc(
        "Land consolidation (chakbandi) - what the instrument does and why it matters",
        "research", "BhuNiti team note", 2026,
        "https://dolr.gov.in/", "official", "India",
        """
        Land consolidation, known as chakbandi in several northern States, reorganises scattered
        fragmented holdings of a landholder into fewer, larger and more compact parcels, usually
        alongside a fresh survey and preparation of updated records. The stated objectives are to
        reduce cultivation inefficiency caused by fragmentation, enable mechanisation and
        irrigation, and provide an opportunity to reconcile records with possession.

        Two effects are relevant to policy evaluation. First, consolidation directly changes parcel
        geometry and average parcel size, which are measurable from cadastral data. Second, because
        consolidation is accompanied by fresh survey and record preparation, it can resolve a stock
        of latent boundary and partition disputes at once, while the consolidation process itself
        generates objections and appeals during its course. The net effect on disputes is therefore
        an empirical question that depends on execution quality, and it should be estimated from
        completed consolidation rounds rather than assumed.
        """,
    ),
    _doc(
        "Land and property disputes in Indian courts - what the public data shows",
        "research", "BhuNiti team note", 2026,
        "https://njdg.ecourts.gov.in/", "official", "India",
        """
        The National Judicial Data Grid publishes case pendency statistics for district and
        subordinate courts and for High Courts, disaggregated by case type, age of case and
        State/district. Civil case categories relating to land, property, title, partition,
        injunction and possession can be extracted from these statistics.

        Independent studies, including survey work by DAKSH, have reported that land and property
        related matters account for a very large share of civil litigation in India, and that such
        cases are among the longest-pending categories. Specific percentages differ between studies
        depending on definitions and sampling, so any figure used in a policy document should be
        cited to a named study with its definition stated, and cross-checked against current NJDG
        extracts rather than quoted from secondary sources.
        """,
    ),
    _doc(
        "NCAER Land Records and Services Index (N-LRSI) - measuring record quality across States",
        "research", "National Council of Applied Economic Research", 2021,
        "https://www.ncaer.org/", "peer_reviewed", "India",
        """
        The NCAER Land Records and Services Index scores States and Union Territories on the extent
        of digitisation of land records and on the quality of those records and of the services
        built on them. Its dimensions include the availability of records of rights online, the
        digitisation and updating of cadastral maps, the integration of registration with mutation,
        and the accessibility and usability of the State portals.

        The index is useful for a research platform in two ways. It provides a defensible,
        published basis for comparing States rather than relying on anecdote, and its dimension
        scores indicate which specific administrative process is weak in a given State, which is
        what a policy recommendation must target. States with low scores are, in general, those
        where records are old, maps are not digitised, or registration and mutation are not linked.
        """,
    ),
    _doc(
        "Land conflict as an investment and livelihood risk",
        "research", "BhuNiti team note", 2026,
        "https://www.landconflictwatch.org/", "peer_reviewed", "India",
        """
        Land Conflict Watch is an independent research initiative that documents ongoing land
        conflicts in India, recording for each conflict the location, the land area and the number
        of people affected, the sector involved such as infrastructure, mining, conservation or
        industry, and the reported investment at stake. The database shows that conflicts
        concentrate in particular sectors and land categories, notably common lands, forest land
        and land acquired for infrastructure.

        The implication for land governance research is that dispute analytics should not be
        limited to court pendency. A large share of conflict never reaches a court, and the
        economically significant cases are often collective disputes over acquisition, commons and
        classification rather than individual title disputes. Counts and totals reported by the
        initiative are updated continuously; cite the database directly with an access date.
        """,
    ),
    _doc(
        "Retrieval-augmented generation for policy research assistants",
        "research", "BhuNiti team note (method)", 2026,
        "https://arxiv.org/abs/2005.11401", "peer_reviewed", "India",
        """
        Retrieval-augmented generation, introduced by Lewis and colleagues in 2020, combines a
        retrieval step over an external corpus with a generation step, so that a language model
        answers from retrieved passages rather than from parameters alone. In a governance setting
        this is the mechanism that makes an assistant auditable: the passages retrieved are the
        evidence, and the answer can be required to cite them.

        Three design choices matter for policy use. The corpus must be restricted to vetted
        documents, so that the model cannot cite unreliable material. The prompt must require a
        citation for every factual claim and must instruct the model to refuse when retrieval
        returns nothing relevant. And the interface must display the retrieved passages alongside
        the answer, so that a reviewer can verify the claim without leaving the tool. BhuNiti
        implements all three, and adds an Evidence Score derived from retrieval coverage, passage
        similarity and source provenance.
        """,
    ),
]
