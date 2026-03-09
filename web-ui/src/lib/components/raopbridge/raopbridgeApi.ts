import {ResonanceAPI} from '$lib/api';

export const enum VolumeMode {
	IGNORED = 0,  // fixed
	HARDWARE = 2,  // device
	SOFTWARE = 1	// gain
}

export interface CommonOptions {
	streambuf_size: number,
	output_size: number,
	enabled: boolean,
	codecs: string[],
	sample_rate: number,
	resolution: null,
	resample: boolean,
	resample_options: null,
	volume_mode: VolumeMode,
	player_volume: number,
	volume_mapping: [number, number][],
	volume_feedback: boolean,
	mute_on_pause: boolean,
	send_metadata: boolean,
	send_coverart: boolean,
	auto_play: boolean,
	idle_timeout: number,
	remove_timeout: boolean,
	alac_encode: boolean,
	encryption: boolean,
	read_ahead: number,
	server: string
}


export interface Device {
	udn: string
	name: string
	friendly_name: string
	mac: string
	enabled: boolean
	common: CommonOptions
}

export interface PluginStatus {
	plugin: 'enabled' | 'disabled';
	bridge: 'active' | 'inactive';
}

export interface PluginSettingsData {
	// Network
	bin: string;
	pid_file: string;
	interface: string;
	server: string;
	active_at_startup: boolean;
	config: string;
	auto_save: boolean;
	logging_enabled: boolean;
	logging_file: string;
	debug_enabled: boolean;
	debug_category: string;
	debug_level: string;
}


class RaopbridgeApi extends ResonanceAPI {

	constructor(baseUrl = "") {
		super(baseUrl);
	}

	async activate(): Promise<boolean> {
		const response: Response = await fetch(`${this.baseUrl}/api/raopbridge/activate`, {
			method: "POST"
		});
		if (!response.ok) {
			throw new Error(`HTTP error: ${response.status}`);
		}
		const data = await response.json();
		return data.result;
	}

	async deactivate(): Promise<boolean> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/deactivate`, {
			method: "POST"
		});
		if (!response.ok) {
			throw new Error(`HTTP error: ${response.status}`);
		}
		const data = await response.json();
		return data.result;
	}

	async getRaopBridgeSettings(): Promise<PluginSettingsData> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/settings`);
		if (!response.ok) {
			throw new Error(`HTTP error: ${response.status}`);
		}
		return await response.json() as PluginSettingsData;
	}

	async updateRaopBridgeSettings(updates: Partial<PluginSettingsData>,): Promise<any> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/settings`, {
			method: "PATCH", headers: {"Content-Type": "application/json"}, body: JSON.stringify(updates),
		});
		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({detail: response.statusText}));
			throw new Error(error.detail || `Failed to update plugin settings: ${response.status}`,);
		}
		return await response.json();
	}

	async getPluginAdvancedSettings(): Promise<CommonOptions> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/settings/advanced`);
		if (!response.ok) {
			throw new Error(`HTTP error: ${response.status}`);
		}
		const data = await response.json() as {options: CommonOptions};
		return data.options
	}

	async getBinOptions(): Promise<string[]> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/bin-options`);
		if (!response.ok) {
			throw new Error(`HTTP error: ${response.status}`);
		}
		return await response.json() as string[];
	}

	async getPluginStatus(): Promise<PluginStatus> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/status`);
		if (!response.ok) {
			throw new Error(`HTTP error: ${response.status}`);
		}
		return await response.json() as PluginStatus;
	}

	async getDevices(): Promise<Device[]> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/device`);
		if (!response.ok) {
			throw new Error(`HTTP error: ${response.status}`);
		}
		const data = await response.json() as {devices: Device[]};
		return data.devices;
	}

	async updateDevice(device: Device): Promise<Device> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/device/${device.udn}`, {
			method: "PUT", headers: {"Content-Type": "application/json"}, body: JSON.stringify(device),
		});
		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({detail: response.statusText}));
			throw new Error(error.detail || `Failed to update plugin device: ${response.status}`,);
		}
		return await response.json() as Device;
	}

	async deleteDevice(device: Device): Promise<boolean> {
		const response = await fetch(`${this.baseUrl}/api/raopbridge/device/${device.udn}`, {
			method: "DELETE",
		});
		if (!response.ok) {
			const error = await response
				.json()
				.catch(() => ({detail: response.statusText}));
			throw new Error(error.detail || `Failed to remove plugin device: ${response.status}`,);
		}
		return true;
	}
}

export const raopbridgeApi = new RaopbridgeApi();
