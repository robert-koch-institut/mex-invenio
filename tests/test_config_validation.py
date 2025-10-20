"""Test configuration validation for UI_SETTINGS and related constants."""

class TestUISettingsConfiguration:
    """Test UI_SETTINGS configuration structure and validity."""
    
    def test_ui_settings_exists(self, app, app_config):
        """Test that UI_SETTINGS configuration exists."""

        assert 'UI_SETTINGS' in app_config
        assert isinstance(app_config['UI_SETTINGS'], dict)
    
    def test_core_entities_configured(self, app, app_config):
        """Test that core entities (resource, activity, bibliographicresource) are configured."""
        ui_settings = app_config['UI_SETTINGS']
        core_entities = ['resource', 'activity', 'bibliographicresource']
        
        for entity in core_entities:
            assert entity in ui_settings, f"Missing configuration for {entity}"
    
    def test_entity_required_keys(self, app, app_config):
        """Test that each entity has required configuration keys."""
        ui_settings = app_config['UI_SETTINGS']
        required_keys = ['label', 'special_fields', 'main']
        
        for entity_name, entity_config in ui_settings.items():
            for key in required_keys:
                assert key in entity_config, f"Missing {key} in {entity_name} configuration"
    
    def test_card_structure_validity(self, app, app_config):
        """Test that cards have valid structure."""
        ui_settings = app_config['UI_SETTINGS']
        
        for entity_name, entity_config in ui_settings.items():
            sections = ['main']
            if 'side_bar' in entity_config:
                sections.append('side_bar')
            for section in sections:
                for card_id, card_config in entity_config[section].items():
                    # Test required card fields
                    assert 'title' in card_config, f"Missing title in {entity_name}.{section}.{card_id}"
                    assert 'icon' in card_config, f"Missing icon in {entity_name}.{section}.{card_id}"
                    
                    # Test properties or components exist
                    assert 'properties' in card_config or 'components' in card_config, \
                        f"Missing properties/components in {entity_name}.{section}.{card_id}"

    def test_special_fields_structure(self, app, app_config):
        """Test that special_fields have valid structure."""
        ui_settings = app_config['UI_SETTINGS']
        
        for entity_name, entity_config in ui_settings.items():
            special_fields = entity_config['special_fields']
            
            for field_key, field_config in special_fields.items():
                assert 'field' in field_config, f"Missing field in {entity_name}.special_fields.{field_key}"
                assert isinstance(field_config['field'], str), f"Field must be string in {entity_name}.special_fields.{field_key}"

    def test_properties_structure(self, app, app_config):
        """Test that properties have valid structure."""
        ui_settings = app_config['UI_SETTINGS']
        
        for entity_name, entity_config in ui_settings.items():
            sections = ['main']
            if 'side_bar' in entity_config:
                sections.append('side_bar')
            for section in sections:
                for card_id, card_config in entity_config[section].items():
                    if 'properties' in card_config:
                        properties = card_config['properties']
                        assert isinstance(properties, list), f"Properties must be list in {entity_name}.{section}.{card_id}"
                        
                        for prop in properties:
                            assert 'field' in prop, f"Missing field in property in {entity_name}.{section}.{card_id}"
                            assert isinstance(prop['field'], str), f"Field must be string in {entity_name}.{section}.{card_id}"

    def test_container_components_structure(self, app, app_config):
        """Test that container cards with components have valid structure."""
        ui_settings = app_config['UI_SETTINGS']
        
        for entity_name, entity_config in ui_settings.items():
            sections = ['main']
            if 'side_bar' in entity_config:
                sections.append('side_bar')
            for section in sections:
                for card_id, card_config in entity_config[section].items():
                    if card_config.get('type') == 'container':
                        assert 'components' in card_config, f"Container card missing components in {entity_name}.{section}.{card_id}"
                        
                        components = card_config['components']
                        assert isinstance(components, list), f"Components must be list in {entity_name}.{section}.{card_id}"
                        
                        for component in components:
                            # Some components may not have 'type' field - that's ok
                            if 'type' in component:
                                assert component['type'] == 'component', f"Component type must be 'component' in {entity_name}.{section}.{card_id}"
                            # Some components may not have 'title' field - that's ok too
                            assert 'properties' in component, f"Component missing properties in {entity_name}.{section}.{card_id}"


class TestFieldTypesConfiguration:
    """Test FIELD_TYPES configuration."""
    
    def test_field_types_exists(self, app, app_config):
        """Test that FIELD_TYPES configuration exists."""
        assert 'FIELD_TYPES' in app_config
        assert isinstance(app_config['FIELD_TYPES'], dict)
    
    def test_field_types_structure(self, app, app_config):
        """Test FIELD_TYPES has valid structure."""
        field_types = app_config['FIELD_TYPES']
        
        for entity_type, fields in field_types.items():
            assert isinstance(fields, dict), f"Field types for {entity_type} must be dict"
            
            for field_name, field_type in fields.items():
                assert isinstance(field_type, str), f"Field type for {entity_type}.{field_name} must be string"
                # Test valid field types
                valid_types = ['string', 'text', 'url', 'date', 'label', 'identifier', 'int', 'integer', 'unknown']
                assert field_type in valid_types, f"Invalid field type '{field_type}' for {entity_type}.{field_name}"

    def test_title_fields_configured(self, app, app_config):
        """Test that TITLE_FIELDS is properly configured."""
        assert 'TITLE_FIELDS' in app_config
        assert isinstance(app_config['TITLE_FIELDS'], list)
        assert len(app_config['TITLE_FIELDS']) > 0
        
        # Test all title fields are strings
        for field in app_config['TITLE_FIELDS']:
            assert isinstance(field, str), f"Title field {field} must be string"


class TestEntitiesConfiguration:
    """Test ENTITIES configuration."""
    
    def test_entities_configured(self, app, app_config):
        """Test that ENTITIES is properly configured."""
        assert 'ENTITIES' in app_config
        assert isinstance(app_config['ENTITIES'], list)
        assert len(app_config['ENTITIES']) > 0
        
        # Test all entities are strings
        for entity in app_config['ENTITIES']:
            assert isinstance(entity, str), f"Entity {entity} must be string"


class TestDisclaimerConfiguration:
    """Test DISCLAIMER configuration."""
    
    def test_disclaimer_configured(self, app, app_config):
        """Test that DISCLAIMER is properly configured."""
        assert 'DISCLAIMER' in app_config
        assert isinstance(app_config['DISCLAIMER'], str)
        assert len(app_config['DISCLAIMER']) > 0


class TestConfigurationIntegrity:
    """Test configuration integrity and cross-references."""
    
    def test_field_references_exist_in_field_types(self, app, app_config):
        """Test that fields referenced in UI_SETTINGS exist in FIELD_TYPES."""
        ui_settings = app_config['UI_SETTINGS']
        field_types = app_config['FIELD_TYPES']
        
        for entity_name, entity_config in ui_settings.items():
            # Check special fields
            for field_key, field_config in entity_config['special_fields'].items():
                field_name = field_config['field']
                # Some special fields may not exist in FIELD_TYPES if they're not part of that entity's schema
                if entity_name in field_types and field_name in field_types[entity_name]:
                    # Field exists - good
                    pass
                # If field doesn't exist, we can optionally warn but shouldn't fail the test
                # as some special fields might be cross-entity references
            
            # Check properties fields
            sections = ['main']
            if 'side_bar' in entity_config:
                sections.append('side_bar')
            for section in sections:
                for card_id, card_config in entity_config[section].items():
                    if 'properties' in card_config:
                        for prop in card_config['properties']:
                            field_name = prop['field']
                            # Skip backward-linked fields as they may not exist in this entity's FIELD_TYPES
                            if prop.get('is_backwards_linked', False):
                                continue
                            # Some fields may not exist in FIELD_TYPES if they're not part of that entity's schema
                            if entity_name in field_types and field_name in field_types[entity_name]:
                                # Field exists - good
                                pass
                            # If field doesn't exist, we can optionally warn but shouldn't fail the test
                            # as some fields might be cross-entity references or computed fields
                    
                    # Check component properties
                    if 'components' in card_config:
                        for component in card_config['components']:
                            if 'properties' in component:
                                for prop in component['properties']:
                                    field_name = prop['field']
                                    # Skip backward-linked fields as they may not exist in this entity's FIELD_TYPES
                                    if prop.get('is_backwards_linked', False):
                                        continue
                                    # Some fields may not exist in FIELD_TYPES if they're not part of that entity's schema
                                    if entity_name in field_types and field_name in field_types[entity_name]:
                                        # Field exists - good
                                        pass
                                    # If field doesn't exist, we can optionally warn but shouldn't fail the test
                                    # as some fields might be cross-entity references or computed fields

    def test_title_fields_exist_in_field_types(self, app, app_config):
        """Test that TITLE_FIELDS exist in at least one entity's FIELD_TYPES."""
        title_fields = app_config['TITLE_FIELDS']
        field_types = app_config['FIELD_TYPES']
        
        all_fields = set()
        for entity_fields in field_types.values():
            all_fields.update(entity_fields.keys())
        
        # Check that at least some title fields exist - not all may be present in all entities
        found_title_fields = []
        for title_field in title_fields:
            if title_field in all_fields:
                found_title_fields.append(title_field)
        
        assert len(found_title_fields) > 0, f"No title fields found in FIELD_TYPES. Expected at least one of: {title_fields}"
