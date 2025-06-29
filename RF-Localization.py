import dataclasses
import math
import os
import re
import folium
import folium.plugins
import argparse

@dataclasses.dataclass
class Particle:
    longitude                           : float
    latitude                            : float
    rssi                                : float
    weight                              : float

class ParticleFilter:
        def __init__(self, data_set) -> None:
                self.data_set           = data_set
                self.networks           = {}

        def get_networks(self) -> None:
                for capture in self.data_set:
                        capture         = capture.split(",")
                        self.add_data(capture)

        def add_data(self, capture: list[str]) -> None:
                ssid                    = capture[5]
                bssid                   = capture[3]
                longitude               = capture[1]
                latitude                = capture[2]
                rssi                    = capture[8]

                longitude, latitude, rssi = float(longitude), float(latitude), float(rssi)

                weight = self.convert_weight(rssi)

                particle                = Particle(longitude, latitude, rssi, weight)
                self.networks.setdefault(ssid, {}).setdefault(bssid, []).append(particle)

        def convert_weight(self, rssi: float) -> float:
                estimated_distance      = 1.0 * 10 ** ((-30.0 - rssi) / (10 * 2.0))
                weight                  = 1.0 / (estimated_distance**2 + 1e-6)

                return weight

        def normalize_weights(self) -> None:
                for ssid, bssids in self.networks.items():
                        for bssid, particles in bssids.items():
                                total          = sum(particle.weight for particle in particles)
        
                                for particle in particles:
                                        particle.weight /= total

def create_heatmaps(networks: dict[str, dict[str, list[Particle]]]) -> None:
        for ssid, bssids in networks.items():
                if not ssid:
                        ssid            = "Unassociated"

                ssid                    = re.sub(r"\W+", "_", ssid)
                all_particles           = []

                for particles in bssids.values():
                        for particle in particles:
                                all_particles.append(particle)

                center_latitude                 = 0
                center_longitude                = 0
        
                for particle in all_particles:
                        center_latitude        += particle.latitude
                        center_longitude       += particle.longitude

                particles_length                = len(all_particles)
                center_latitude                /= particles_length
                center_longitude               /= particles_length

                folium_map                      = folium.Map(
                        location                = [center_latitude, center_longitude],
                        zoom_start              = 19,
                        min_zoom                = 17,
                        max_zoom                = 21
                )
                google_tiles                    = folium.TileLayer(
                        tiles                   = "http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                        attr                    = "Silentis",
                        max_zoom                = 21
                )
                google_tiles.add_to(folium_map)

                for bssid, particles in bssids.items():
                        particle_datas          = []

                        for particle in particles:
                                particle_data   = [particle.latitude, particle.longitude, particle.weight]
                                particle_datas.append(particle_data)
                        
                        feature                 = folium.FeatureGroup(
                                name            = bssid,
                                show            = False
                        )
                        heat_map                = folium.plugins.HeatMap(
                                particle_datas,
                                radius          = 25
                        )
                        heat_map.add_to(feature)
                        feature.add_to(folium_map)

                folium.LayerControl(collapsed=False).add_to(folium_map)

                filename = f"heatmaps/{ssid}.html"
                folium_map.save(filename)


def main():
        parser                          = argparse.ArgumentParser(description="RF Localizer")
        parser.add_argument("--file", "-f", required=True)
        args                            = parser.parse_args()

        with open(args.file, "r") as f:
                capture                 = f.read().splitlines()[1:]

        particle_filter                 = ParticleFilter(capture)
        particle_filter.get_networks()
        particle_filter.normalize_weights()
        os.makedirs("heatmaps", exist_ok=True)
        create_heatmaps(particle_filter.networks)

if __name__ == "__main__":
    main()