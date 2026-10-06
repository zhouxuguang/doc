from pathlib import Path
import subprocess, shlex, re

ROOT = Path('/Users/zhouxuguang/work/mycode/GNXMapEngine')
BUILD = ROOT / 'build-map-native'
OUT = Path(__file__).resolve().parent / 'capture_demo'
OUT.mkdir(exist_ok=True)
SRC = ROOT / 'GNXEngine/demo/atmosphere'
for name in ['AtmosphereFrameWork.cpp','AtmosphereFrameWork.h','AtmospherePreset.cpp','AtmospherePreset.h']:
    s = (SRC/name).read_text()
    if name.endswith('.h') and name.startswith('AtmosphereFrameWork'):
        s = s.replace('private:', 'public:')
    if name == 'AtmosphereFrameWork.cpp':
        s = s.replace('SetImGuiEnabled(true);', 'SetImGuiEnabled(false);')
        s = s.replace('mAtmosphere->Initialize(mAtmosphereParameters, 5);', 'mAtmosphere->Initialize(mAtmosphereParameters, (unsigned)mScatteringOrders);')
        s = s.replace('mScatteringOrders = 5;', '// capture: scattering order configured by the driver')
    (OUT/name).write_text(s)
for name in ['ScreenshotUtil.cpp','ScreenshotUtil.h']:
    (OUT/name).write_bytes((ROOT/'GNXMapEngine'/name).read_bytes())
(OUT/'main.cpp').write_text(r'''
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
''')
commands = subprocess.check_output(['ninja','-C',str(BUILD),'-t','commands','atmosphere'],text=True).splitlines()
compile_base = next(shlex.split(c) for c in commands if 'AtmosphereFrameWork.cpp.o' in c and ' -c ' in c)
for name in ['main.cpp','AtmosphereFrameWork.cpp','AtmospherePreset.cpp','ScreenshotUtil.cpp']:
    cmd = compile_base[:]
    cmd[cmd.index('-o')+1] = str(OUT/(name+'.o'))
    cmd[cmd.index('-c')+1] = str(OUT/name)
    if '-MF' in cmd: cmd[cmd.index('-MF')+1] = str(OUT/(name+'.d'))
    if '-MT' in cmd: cmd[cmd.index('-MT')+1] = str(OUT/(name+'.o'))
    subprocess.run(cmd,cwd=BUILD,check=True)
link = shlex.split(commands[-1])
if '&&' in link:
    start = next(i for i,x in enumerate(link) if x.endswith('clang++') or x.endswith('c++'))
    end = link.index('&&',start) if '&&' in link[start:] else len(link)
    link = link[start:end]
link = [x for x in link if not ('engine/demo/atmosphere/CMakeFiles/atmosphere.dir/' in x and x.endswith('.o'))]
link[link.index('-o')+1] = str(OUT/'atmosphere_capture')
link += [str(OUT/(name+'.o')) for name in ['main.cpp','AtmosphereFrameWork.cpp','AtmospherePreset.cpp','ScreenshotUtil.cpp']]
subprocess.run(link,cwd=BUILD,check=True)
print(OUT/'atmosphere_capture')
