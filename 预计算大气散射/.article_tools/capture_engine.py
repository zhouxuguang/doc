from pathlib import Path
import subprocess, os, json, hashlib, math

HERE=Path(__file__).resolve().parent
WORK=HERE.parent
ROOT=Path('/Users/zhouxuguang/work/mycode/GNXMapEngine')
IMAGES=WORK/'atmosphere_scattering_images'
CAP=HERE/'capture_demo/atmosphere_capture'
MAP=ROOT/'build-map-native/GNXMapEngine.app/Contents/MacOS/GNXMapEngine'
cases=[
    dict(name='demo_day',kind='demo',zenith=1.0,orders=5),
    dict(name='demo_sunset',kind='demo',zenith=1.56,orders=5),
    dict(name='demo_twilight_5',kind='demo',zenith=1.64,orders=5),
    dict(name='demo_twilight_1',kind='demo',zenith=1.64,orders=1),
    dict(name='earth_global',kind='map',distance=15000000,pitch=0),
    dict(name='earth_orbit',kind='map',distance=1000000,pitch=65),
    dict(name='earth_horizon',kind='map',distance=20000,pitch=85),
]
manifest={'date':'2026-10-05','algorithm':'LegacyPrecomputed','exposure':5.0,'backend':'macOS Metal','captures':[],
          'engine_root':str(ROOT),'source_hashes':{},'notes':'Demo capture uses copied demo source with UI disabled and preset parameters; original renderer, shaders and repository source are unchanged.'}
for repo,label in [(ROOT,'map'),(ROOT/'GNXEngine','engine')]:
    manifest[label+'_commit']=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
for path in [ROOT/'GNXEngine/Engine/Shader/built-in/Atmosphere/AtmosphereCommon.hlsl',
             ROOT/'GNXEngine/Engine/Runtime/RenderSystem/include/Atmosphere/AtmosphereRenderer.cpp',
             ROOT/'GNXEngine/data_asset/Shader/AtmosphereDemo/Sky.msl_macos.gnxasset']:
    manifest['source_hashes'][str(path.relative_to(ROOT))]=hashlib.sha256(path.read_bytes()).hexdigest()
for case in cases:
    dest=IMAGES/(case['name']+'.png')
    env=os.environ.copy(); env['MTL_DEBUG_LAYER']='0'
    if case['kind']=='demo':
        cmd=[str(CAP),str(case['zenith']),str(case['orders']),str(dest)]
        z=case['zenith'];az=2.9
        case.update(azimuth=az,camera=[8910,905,893],target=[0,0,0],frames=120,
                    sun_direction=[math.sin(z)*math.cos(az),math.cos(z),-math.sin(z)*math.sin(az)])
    else:
        values={'GNX_MAP_ATMOSPHERE':'1','GNX_MAP_ATMOSPHERE_ALGORITHM':'legacy','GNX_MAP_PANEL':'0',
                'GNX_MAP_TARGET_LON':'110','GNX_MAP_TARGET_LAT':'23','GNX_MAP_EYE_DISTANCE':str(case['distance']),
                'GNX_MAP_PITCH':str(case['pitch']),'GNX_MAP_SCREENSHOT':str(dest),'GNX_MAP_SCREENSHOT_FRAMES':'180'}
        env.update(values); cmd=[str(MAP)]; length=math.sqrt(.5**2+.3**2+.8**2)
        case.update(target_lon=110,target_lat=23,orders=5,frames=180,
                    sun_direction=[.5/length,.3/length,.8/length])
    log=HERE/'qa'/(case['name']+'.log')
    print('Capturing',case['name'],flush=True)
    with log.open('w') as f:
        r=subprocess.run(cmd,cwd=WORK,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=150)
    lines=log.read_text(errors='replace').splitlines()
    case.update(exit_code=r.returncode,file=dest.name,log=str(log.relative_to(WORK)),
                evidence=[s for s in lines if 'precompute finished' in s or 'CAPTURE_DONE' in s or '[截图]' in s or '视点:' in s or 'CaptureFrameToPng: saved' in s])
    case['success']=r.returncode==0 and dest.exists()
    if dest.exists(): case['image_sha256']=hashlib.sha256(dest.read_bytes()).hexdigest()
    manifest['captures'].append(case)
    (IMAGES/'capture_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    print(case['name'],'OK' if case['success'] else 'FAILED',flush=True)
    if not case['success']: print('\n'.join(lines[-15:]),flush=True)
