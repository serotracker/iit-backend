import tests.factories as factories


def delete_records(session, records):
    for record in records:
        session.delete(record)
    session.commit()
    return


def insert_record(session):
    # Insert main record into airtable source
    new_airtable_source_record = factories.airtable_source_factory(session)
    source_id = new_airtable_source_record.source_id
    country_id = new_airtable_source_record.country_id

    # Insert joined record into age bridge table
    new_age_bridge_record = factories.age_bridge_factory(session, source_id=source_id)
    age_id = new_age_bridge_record.age_id

    # Insert joined record into age table
    factories.age_factory(session, age_id=age_id)

    # Insert joined record into approving regulator bridge table
    new_approving_regulator_bridge_record = factories.approving_regulator_bridge_factory(session, source_id=source_id)
    approving_regulator_id = new_approving_regulator_bridge_record.approving_regulator_id

    # Insert joined record into approving regulator table
    factories.approving_regulator_factory(session, approving_regulator_id=approving_regulator_id)

    # Insert joined record into city bridge table
    new_city_bridge_record = factories.city_bridge_factory(session, source_id=source_id)
    city_id = new_city_bridge_record.city_id

    # Insert joined record into city table
    factories.city_factory(session, city_id=city_id)

    # Insert joined record into country table
    factories.country_factory(session, country_id=country_id)

    # Insert joined record into population group bridge table
    new_population_group_record = factories.population_group_bridge_factory(session, source_id=source_id)
    population_group_id = new_population_group_record.population_group_id

    # Insert joined record into population group table
    factories.population_group_factory(session, population_group_id=population_group_id)

    # Insert joined record into state bridge table
    new_state_record = factories.state_bridge_factory(session, source_id=source_id)
    state_id = new_state_record.state_id

    # Insert joined record into state table
    factories.state_factory(session, state_id=state_id)

    # Insert joined record into specimen type bridge table
    new_specimen_type_record = factories.specimen_type_bridge_factory(session, source_id=source_id)
    specimen_type_id = new_specimen_type_record.specimen_type_id

    # Insert joined record into specimen type table
    factories.specimen_type_factory(session, specimen_type_id=specimen_type_id)

    # Insert joined record into test type bridge table
    new_test_type_record = factories.test_type_bridge_factory(session, source_id=source_id)
    test_type_id = new_test_type_record.test_type_id

    # Insert joined record into test type table
    factories.test_type_factory(session, test_type_id=test_type_id)

    # Insert joined record into test manufacturer bridge table
    new_test_manufacturer_record = factories.test_manufacturer_bridge_factory(session, source_id=source_id)
    test_manufacturer_id = new_test_manufacturer_record.test_manufacturer_id

    # Insert joined record into test manufacturer table
    factories.test_manufacturer_factory(session, test_manufacturer_id=test_manufacturer_id)
    return
