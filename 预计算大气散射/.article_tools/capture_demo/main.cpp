
#include "AtmosphereFrameWork.h"
#include "ScreenshotUtil.h"
#include "Runtime/GNXEngine/include/RenderWindow.h"
#include <cstdlib>
#include <iostream>
class CaptureDemo : public AtmosphereFrameWork {
public:
    using AtmosphereFrameWork::AtmosphereFrameWork;
    std::string output; int frame = 0; bool saved = false;
    void RenderFrame() override {
        AtmosphereFrameWork::RenderFrame();
        ++frame;
        if (frame >= 120 && mAtmosphere && mAtmosphere->IsPrecomputed()) {
            auto window = GNXEngine::GetRenderWindow();
            saved = CaptureFrameToPng(RenderSystem::SceneManager::GetInstance(), nullptr,
                window->GetWidth(), window->GetHeight(), output);
            std::cout << "CAPTURE_DONE sun_zenith=" << mSunZenith
                << " sun_azimuth=" << mSunAzimuth << " orders=" << mScatteringOrders
                << " frames=" << frame << " saved=" << saved << std::endl;
            window->RequestClose();
        }
    }
};
int main(int argc, char** argv) {
    if (argc != 4) return 2;
    GNXEngine::WindowProps props("GNXEngine Atmosphere - Article Capture",1280U,720U);
    CaptureDemo app(props);
    app.mSunZenith = std::strtof(argv[1], nullptr);
    app.mSunAzimuth = 2.9f;
    app.mScatteringOrders = std::atoi(argv[2]);
    app.mPendingScatteringOrders = app.mScatteringOrders;
    app.output = argv[3];
    app.RunLoop();
    return app.saved ? 0 : 3;
}
