<template>
	<div :style="listItemStyle(depth)">
		<header>
			<h3 class="title" @click="visible = !visible" :aria-controls="domId + '-props'" :aria-expanded="visible ? 'true' : 'false'">
				<!--<font-awesome-icon v-if="!visible" :icon="expandArrow" class="text-dark"/>-->
				{{ uiTitle }}
			</h3>
		</header>
		<section>
			<b-list-group flush>
				<b-list-group-item class="border-0" v-for="propName in sortedProps" :key="propName">
					<TabSelector
						:required="(schema.required || []).includes(propName)"
						:schema="schema['properties'][propName]"
						:path="newPath('properties/' + propName)"
						:value="value[propName]"
						:parent="value"
						:property="propName"
						:tab="myTab"
						:activeTab="activeTab"
						:depth="depth"
						:key="propName"
						v-if="shouldCreateProp(propName)" />
						<b-btn @click="addProp(propName)" v-else-if="isPostponedProp(propName)">add {{ propName }}</b-btn>
				</b-list-group-item>
			</b-list-group>
		</section>
	</div>
	<!--<b-card no-body header-class="with-fd-bg" class="my-3">
		<h2 slot="header" @click="visible = !visible" :aria-controls="domId + '-props'" :aria-expanded="visible ? 'true' : 'false'">
			<font-awesome-icon v-if="!visible" :icon="expandArrow" class="text-dark"/> {{ uiTitle }}
		</h2>

		<b-collapse :id="domId + '-props'" v-model="visible">
			<b-card-body>
				<p class="card-text text-muted" v-if="uiDescription"><sup><font-awesome-icon icon="quote-left" class="text-muted" /></sup> {{ uiDescription }}</p>
			</b-card-body>

			<b-list-group flush>
				<b-list-group-item class="border-0" v-for="propName in sortedProps" :key="propName">
					<TabSelector :schema="schema['properties'][propName]" :path="newPath('properties/' + propName)" :value="value[propName]" :parent="value" :property="propName" :tab="myTab" :activeTab="activeTab" :depth="depth" :key="propName" v-if="shouldCreateProp(propName)"></TabSelector>
					<b-btn @click="addProp(propName)" v-else>add {{ propName }}</b-btn>

					TabSelector :schema="propSchema" :path="newPath('properties/' + propName)" :value="value[propName]" :parent="value" :property="propName" :tab="myTab" :activeTab="activeTab"
				:depth="depth" :key="propName"></TabSelector
				</b-list-group-item>
			</b-list-group>
		</b-collapse>
	</b-card>-->
</template>

<style>
div:empty {
	/* background: lime; */
	/* display: none; */
}
</style>

<script>
import vSchemaBase from './base.vue'
import keysWithOrder from '@/lib/keysWithOrder.js'
import BorderColorMixin from '../mixins/border-color-mixin.js'

export default {
	extends: vSchemaBase,
	mixins: [BorderColorMixin],
	name: 'SchemaObject',
	description: "generic object",
	schematype: 'object',
	data: function() {
		return {
			q: "not set",
			visible: true,
		}
	},
	/*
	watch: {
		schema: {
			handler(val) {
				//this.q = this.schema['.q']
				this.q = val['.q'] || "not set 2"
				console.log("OBJECT SCHEMA WATCHER RAN for", this.path, "val:", val)
			},
			deep: true,
		},
	},
	*/
	methods: {
		shouldCreateProp(prop) {
			if (!this.isPostponedProp(prop) && !this.isIgnoredProp(prop)) return true
			if (prop in this.value) return true
			return false
		},
		isPostponedProp(prop) {
			return this.postponedProps.includes(prop)
		},
		isIgnoredProp(prop) {
			return this.ignoredProps.includes(prop)
		},
		addProp(prop) {
			this.$store.commit('addProp', {
				val: this.value,
				prop: prop,
			})
		},
	},
	computed: {
		vState() {
			return this.$store.state.vState
		},
		myState: {
			cache: false,
			get: function() {
				return this.vState[this.path] || {}
			},
		},
		/*
		myState() {
			return this.vState[this.path] || {}
		},
		*/
		sortedProps() {
			if (!this.schema['properties']) {
				return []
			}

			if (typeof this.ui['order'] === 'object') {
				return keysWithOrder(this.schema['properties'], this.ui['order'])
			} else {
				return Object.keys(this.schema['properties'])
			}
		},
		postponedProps() {
			return this.ui['postponed'] || []
		},
		ignoredProps() {
			return this.ui['ignored'] || []
		},
		expandArrow() {
			return this.visible ? "ellipsis-v" : "angle-right"
		},
	},
	created() {
		//console.log("registered components:", this.$options.components)
		//console.log("object:", this, "path:", this.path, "children:", this.$children, "slots:", this.$slots)
		if ('visible' in this.ui) this.visible = this.ui['visible']
		// console.log("xxx Object: jsonPointer:", this.path)
		//, jsonPointer.get(this.path))
	},
}
</script>

<style lang="scss" scoped>
.title {
	margin-left: 20px;
}
</style>
