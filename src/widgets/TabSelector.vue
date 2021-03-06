<template>
	<div class="q-tab-selector">
		<!--
		Tab schema {{ schema.required }}
		Widget {{ widget }}
		this is required {{ required }}
		property was {{ property }}
		-->

		<!-- schema-tab-selector -->
		<div v-if="showWidgets">
			<p>ui widgets</p>
			<select v-model="customWidget">
				<option v-for="(constructor, name) in this.$options.components" :key="constructor">{{ name }}</option>
			</select>
		</div>

		<div v-if="showTypeSelector">
			<p>this schema has multiple possible types; please choose one</p>
			<select v-model="dataType">
				<option disabled value="">Please select one</option>
				<option v-for="type in possibleTypes" :key="type">
					{{ type }}
				</option>
			</select>
		</div>

		<!-- actual component -->
		<!-- keep-alive -->
		<keep-alive>
			<component v-if="activeTab === myTab" :is="widget" v-bind="widgetProps" :required="required" :schema="schema" :path="path" :value="parent[property]" :valtype="dataType" :parent="parent" :property="property" :hasTypeError="hasTypeError" :tab="myTab" :activeTab="activeTab" :depth="newdepth" v-on="$listeners">
				<p>{{ dataType }}</p>
			</component>
			<skip v-else :required="(schema.required || []).includes(property)" :schema="schema" :path="path" :value="parent[property]" :valtype="dataType" :parent="parent" :property="property" :hasTypeError="hasTypeError" :tab="myTab" :activeTab="activeTab" :depth="depth" v-on="$listeners"></skip>
			{{ (schema.required || []).includes(property) }}
		</keep-alive>
		<!-- <div style="color: #eeeeee;">hidden myTab: {{ myTab }} {{ typeof myTab }} tab: {{ tab }} {{ typeof tab }} active: {{ activeTab }} {{ typeof activeTab }}</div> -->

	</div>
</template>

<script>
import SchemaNumber from './Number.vue'
import SchemaString from './String.vue'
import SchemaObject from './Object.vue'
import SchemaArray from './Array.vue'
import SchemaInlineArray from './InlineArray.vue'
import SchemaAnyOf from './anyOf.vue'
import SchemaAllOf from './allOf.vue'
import SchemaOneOf from './oneOf.vue'
import SchemaEnum from './Enum.vue'
import WidgetGoogleMaps from './widget-googlemaps.vue'
import refdataList from './refdata/list.vue'
import i18nString from '@/components/i18nStrings.vue'
import i18nTextarea from '@/components/i18nTextarea.vue'
import TabbedArray from './TabbedArray.vue'
import AutoComplete from './refdata/autocomplete.vue'
import FilePicker from '../filebrowser/FilePicker.vue'
import Skip from './skip.js'
import SelfReferentialObject from './SelfReferentialObject.vue'
import FlatObject from './FlatObject.vue'
import ReferenceData from '../components/ReferenceData.vue'
import DateRange from '../components/DateRange.vue'
import Date from '../components/Date.vue'

const COMBINERS = ['anyOf', 'allOf', 'oneOf', 'not']

export default {
	name: 'TabSelector',
	description: "internal dispatch wrapper",
	widgettype: 'any',
	/*
	props: {
		schema: Object,
	},
	*/
	props: ['schema', 'value', 'path', 'parent', 'property', 'tab', 'activeTab', 'depth', 'required'],
	data: function() {
		return {
			dataType: null,
			hasTypeError: false,
			verbose: false,
			showWidgets: false,
			customWidget: null,
			cachedPath: null,
		}
	},
	methods: {
		setDataType: function(schemaType) {
			if (typeof schemaType === 'object' && schemaType instanceof Array) {
				this.dataType = schemaType[0]
			} else {
				this.dataType = schemaType
			}
		},
		emptyValue: function() {
			switch (this.dataType) {
			case 'object':
				return {}
			case 'array':
				return []
			case 'null':
				return null
				//default:
			}
			return undefined
		},
		handleCombiners: function() {
			for (let i in COMBINERS) {
				if (!(COMBINERS[i] in this.schema)) continue

				let combiner = COMBINERS[i]

				if (typeof this.schema[combiner] === 'object' && this.schema[combiner] instanceof Array) {
					return 'schema-' + combiner.toLowerCase()
				}

				return undefined
			}
			return undefined
		},
		defaultWidget: function(schemaType) {
			//console.log("schemaType:", schemaType)

			// enum is special because it should handle any type included in its values
			if (this.schema.enum) {
				return 'schema-enum'
			}

			if (this.schema.oneOf) {
				return "schema-oneof"
			}

			switch(schemaType) {
			case 'string':
				return 'schema-string'
			case 'number':
				return 'schema-number'
			case 'integer':
				return 'schema-number'
			case 'object':
				return 'schema-object'
			case 'array': {
				// check if the array has values (strings, numbers, null) or nested objects (array, object)
				// TODO: this only checks "list" validation, not "tuple" validation
				let typeOfItems = this.schema.items && this.schema.items.type && this.schema.items.type || ""
				//let hasValues = typeOfItems !== "array" && typeOfItems !== "object"
				//return hasValues ? 'schema-inline-array' : 'schema-array'
				return 'schema-array'
			}
			case 'boolean':
				return ""
			case 'null':
				return ""
			case undefined:
				return this.handleCombiners() || ""
			default:
				return ""
			}
		},
		vivicate: function(force) {
			if (this.value !== undefined && !force) {
				return
			}


			let target, key // eslint-disable-line no-unused-vars

			// the parent of the root path is the store
			if (this.parent === undefined || this.parent === "") {
				target = this.$store.state
				key = 'record'
			} else {
				target = this.parent
				key = this['property']
			}

			// object and arrays can have children so need to be set to something
			/*
			if (this.schema['type'] === 'object' || this.schema['properties']) {
				this.value = {}
				this.$store.commit('updateValue', { p: target, prop: this.property, val: {} })
				console.log("set value to empty object", this.$store.state.record.title, this.value)
			} else if (this.schema['type'] === 'array') {
				//this.value = []
				this.$store.commit('updateValue', { p: target, prop: this.property, val: [] })
				console.log("set value to empty array")
			}
			*/
			//console.log('updateValue from vivicate', this.parent)

			// if we don't have a parent, we're changing the top level; set the record to the correct empty value
			/*
			if (this.parent === undefined || this.parent === "") {
				console.warn("tab-selector: no parent for", this.path)
				//this.$store.commit('loadData', this.emptyValue())
				return
			}
			*/

			this.$store.commit('initValue', { p: this.parent, prop: this.property, val: this.emptyValue() })
			//this.$store.commit('initValue', { p: this.parent, prop: this.property, val: {} })
			/*
			else {
				this.$set(target, key, "abc")
			}
			*/
		},
	},
	computed: {
		showTypeSelector: function() {
			// schema type can be array or string (or undefined)
			//return this.schema['type'] === undefined || typeof this.schema['type'] === 'object'
			return typeof this.schema['type'] !== 'string'
		},
		possibleTypes: function() {
			if (this.schema['type'] === 'object') {
				return this.schema['type']
			}
			return ["string", "number", "integer", "object", "array", "boolean", "null"]
		},
		widget: function() {
			return this.selectedWidget || this.uiForSchema.widget || this.uiForDef.widget || this.defaultWidget(this.dataType)
		},
		widgetProps: function() {
			return this.uiForSchema.props || this.uiForDef.props || undefined
		},
		/*
		ui: function() {
			return Object.assign({}, this.uiForDef, this.uiForSchema)
		},
		*/
		ui: function() {
			// if there was a $ref, use that ref's ui as default and load this path's on top of it
			if (this.schema['$deref']) {
				return Object.assign({}, this.$store.state.hints[this.schema['$deref']], this.$store.getters.uiForPath(this.path))
			}
			return this.$store.getters.uiForPath(this.path)
		},
		uiForSchema: function() {
			//return this.$store.state.hints[this.path] || this.uiDefHint || {}
			return this.$store.getters.uiForPath(this.path)
		},
		uiForDef: function() {
			return ('$deref' in this.schema && this.$store.state.hints[this.schema['$deref']]) || {}
		},
		uiTab: function() {
			return this.$store.state.hints[this.path] && this.$store.state.hints[this.path]['tab']
		},
		myTab: function() {
			return typeof this.uiTab === 'string' ? this.uiTab : this.tab
		},
		newdepth: function() {
			return 'tab' in this.uiForSchema ? 1 : this.depth + 1
		},
	},
	watch: {
		schema: function() {
			if (this.path !== this.cachedPath) {
				console.warn("selector (" + this.path + "): VNode was recycled!")
			}
			//if (this.$store.state.record === undefined) {
			//if (!this.path && this.value === undefined) {
			if (this.value === undefined) {
				this.setDataType(this.schema['type'])
				this.vivicate()
			}
		},
		/*
		value: function() {
			console.log("selector: value watcher ran")
			//if (this.$store.state.record === undefined) {
			//if (!this.path && this.value === undefined) {
			if (this.value === undefined) {
				console.log("data change, undefined value")
				this.setDataType(this.schema['type'])
				this.vivicate()
			}
			if (this.value !== undefined && this.dataType === 'array' && typeof this.value !== 'object') {
				console.error("[selector/value] array expected for path", this.path, "got:", typeof this.value)
				this.hasTypeError = true
				this.vivicate(true)
			}
			if (this.value !== undefined && this.dataType === 'object' && typeof this.value !== 'object') {
				console.error("[selector/value] array expected for path", this.path, "got:", typeof this.value)
				this.hasTypeError = true
				this.vivicate(true)
			}
		},
		*/
	},
	components: {
		'schema-number': SchemaNumber,
		'schema-string': SchemaString,
		'schema-object': SchemaObject,
		'schema-array': SchemaArray,
		'schema-inline-array': SchemaInlineArray,
		'schema-anyof': SchemaAnyOf,
		'schema-allof': SchemaAllOf,
		'schema-oneof': SchemaOneOf,
		'schema-enum': SchemaEnum,
		'widget-googlemaps': WidgetGoogleMaps,
		'refdata-list': refdataList,
		'reference-data': ReferenceData,
		'i18n-string': i18nString,
		'i18n-textarea': i18nTextarea,
		'tabbed-array': TabbedArray,
		'autocomplete': AutoComplete,
		'filepicker': FilePicker,
		'skip': Skip,
		SelfReferentialObject,
		FlatObject,
		'date-range': DateRange,
		'date': Date,
	},
	created() {
		// fail-safe for inadvertent VNode recycling
		this.cachedPath = this.path
		this.setDataType(this.schema['type'])

		// This should try to catch invalid data in case the schema (outside of the application) has changed
		// and we have stale, deprecated or otherwise invalid data left.
		// TODO: think how to handle this: simply delete invalid value, or set a flag to warn user
		if (this.value !== undefined && this.dataType === 'array' && typeof this.value !== 'object') {
			console.error("[selector/created] array expected for path", this.path, "got:", typeof this.value)
			this.hasTypeError = true
			this.vivicate(true)
		}
		if (this.value !== undefined && this.dataType === 'object' && typeof this.value !== 'object') {
			console.error("[selector/created] object expected for path", this.path, "got:", typeof this.value)
			this.hasTypeError = true
			this.vivicate(true)
		}
		if (this.value === undefined) {
			this.vivicate()
		}
	},
}
</script>
