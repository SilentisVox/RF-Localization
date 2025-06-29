# RF Localization

### 1       Introduction
Our approach to signal source localization uses a particle filter, which is relatively common for a source localization problem. Our specific particle filtering approach derives from Chapter 3 of [1] and uses a generalized likelihood function to account for parameters of RF source which are not known but are assumed to have bounded values.

The use of Unmanned Aerial Systems, UAS, as mobile sensors for RF source localization has been and continues to be explored [2, 3, 4, 5]. A literature review that we recommend may be found in [6]. The work that we present differs from existing methods in three significant ways: 1) We do not rely on directional antennas or known RF parameters; 2) We localize multiple RF sources using real hardware; 3) We use only a Raspberry Pi Zero 2W for sensing.