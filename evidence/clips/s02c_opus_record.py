"""Record S02c Opus-continuation local files and narrow usability flags; never approves footage."""
import csv, hashlib, json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; MAN = ROOT / 'clips.csv'; REC = ROOT / 'evidence/clips/S02c-acquisition.json'
EV = 'evidence/clips/S02c-opus-frame-evidence.md'
EVS = dict.fromkeys(('PJ03', 'N1', 'N2', 'N3', 'ST03'), 'evidence/clips/S02c-integration-r1.md')  # integration round 1 evidence
EVS['BN01'] = 'evidence/clips/S02c-primary-r2.md'  # primary round 2 evidence
UPD = {'BN01': dict(suitability='Real Earth floor bounces: visible unoccluded floor contacts file ~14.13 s and ~14.80 s; post-contact arcs tracked at full 240 fps file rate; handheld drift <=3 px; oblique view, ball size/scale unknown; person elsewhere in file',
                    timebase_status='FILE_240FPS_TITLE_240FPS_NO_BALL_LEVEL_REPEATS_CAPTURE_UNVERIFIED', evidence_path=EVS['BN01'])}
C = 'https://commons.wikimedia.org/wiki/File:'
NEW = [
 dict(clip_id='PD04', experiment='pendulum', title='Blocked-pendulum-slow-motion', source_url=C+'Blocked-pendulum-slow-motion.webm', original_source_url=C+'Blocked-pendulum-slow-motion.webm',
      download_url='https://upload.wikimedia.org/wikipedia/commons/b/b7/Blocked-pendulum-slow-motion.webm', creator='MikeRun', licence='CC-BY-SA-4.0', licence_url='https://creativecommons.org/licenses/by-sa/4.0/',
      attribution='MikeRun - Blocked-pendulum-slow-motion - Wikimedia Commons - CC BY-SA 4.0; retain source and licence links', file='PD04.webm', source_duration_label='20 s', source_resolution='1280x720',
      scale_reference='Pivot and stand visible; no documented length', scale_status='UNVERIFIED', timebase_status='SOURCE_TITLE_SAYS_SLOW_MOTION_FACTOR_UNKNOWN',
      suitability='Blocked (restricted) pendulum; bob and pivot visible; hand release f0-~110; drawn dashed overlay line', capture_group='MIKERUN_BLOCKED_PENDULUM'),
 dict(clip_id='PD06', experiment='pendulum', title='Foucault pendulum utexas motion', source_url=C+'Foucault_pendulum_utexas_motion.webm', original_source_url=C+'Foucault_pendulum_utexas_motion.webm',
      download_url='https://upload.wikimedia.org/wikipedia/commons/5/5f/Foucault_pendulum_utexas_motion.webm', creator='Spheroidite', licence='CC-BY-SA-4.0', licence_url='https://creativecommons.org/licenses/by-sa/4.0/',
      attribution='Spheroidite - Foucault pendulum utexas motion - Wikimedia Commons - CC BY-SA 4.0; retain source and licence links', file='PD06.webm', source_duration_label='9.5 s', source_resolution='1920x1080',
      scale_reference='Top-down view; dial ring tick marks of unknown size', scale_status='UNVERIFIED', timebase_status='CAPTURE_TIMEBASE_UNVERIFIED',
      suitability='Top-down Foucault bob, continuously visible; long pendulum, partial period only; projection geometry unknown', capture_group='UTEXAS_DEV_FOUCAULT'),
 dict(clip_id='RM05', experiment='room_scene', title='Step Inside the Station (4K Clean)', source_url='https://images.nasa.gov/details/Step_Inside_the_Station-4K-Clean', original_source_url='https://images.nasa.gov/details/Step_Inside_the_Station-4K-Clean',
      download_url='https://images-assets.nasa.gov/video/Step_Inside_the_Station-4K-Clean/Step_Inside_the_Station-4K-Clean~small.mp4', creator='NASA (JSC)', licence='PD-USGov-NASA', licence_url='https://www.nasa.gov/nasa-brand-center/images-and-media/',
      attribution='NASA - Step Inside the International Space Station (clean); NASA Image and Video Library; no endorsement implied', file='RM05.mp4', source_duration_label='see ffprobe', source_resolution='source 4K; local small rendition',
      scale_reference='Module hatch/handrail standard sizes not verified here', scale_status='SCENE_ONLY', timebase_status='FILE_FPS_ONLY',
      suitability='Continuous float-through ISS interior; camera translation; astronauts visible (NASA media guidelines, no endorsement); microgravity scene not an Earth room', capture_group='NASA_ISS_TOUR_2022'),
]
NEW += [
 dict(clip_id='ST03', experiment='free_fall', title='Woman dropping apple on ground', source_url='https://www.pexels.com/video/woman-dropping-apple-on-ground-12723966/', original_source_url='https://www.pexels.com/video/woman-dropping-apple-on-ground-12723966/',
      download_url='https://videos.pexels.com/video-files/12723966/12723966-hd_720_1366_30fps.mp4', creator='Roman Odintsov', licence='Pexels License', licence_url='https://www.pexels.com/license/',
      attribution='Roman Odintsov - Woman dropping apple on ground - Pexels (Pexels License); no endorsement implied', file='ST03.mp4', source_duration_label='0:18', source_resolution='2160x4096; local 720x1366 rendition',
      scale_reference='Apple width ~61 px, real size assumed only', scale_status='UNVERIFIED', timebase_status='25P_IN_30P_REPEATS_VERIFIED_CAPTURE_SLOWMO_UNKNOWN',
      suitability='Real hand-released apple, static camera, continuous unoccluded fall f58-76 onto pillow; probable slow motion so playback acceleration is not g', capture_group='PEXELS_ODINTSOV_APPLE'),
 dict(clip_id='PJ03', experiment='projectile', title='Ballistische Kurve', source_url=C+'Ballistische_Kurve.webm', original_source_url=C+'Ballistische_Kurve.webm',
      download_url='https://upload.wikimedia.org/wikipedia/commons/1/14/Ballistische_Kurve.webm', creator='Rhetos; end card Mathe-AC Lernwerkstatt Aachen', licence='CC-BY-SA-4.0', licence_url='https://creativecommons.org/licenses/by-sa/4.0/',
      attribution='Rhetos - Ballistische Kurve - Wikimedia Commons - CC BY-SA 4.0; video end card: (c) 2025 Mathe-AC Lernwerkstatt Aachen, CC BY 4.0 - credit both and keep end card', file='PJ03.webm', source_duration_label='73.4 s', source_resolution='1920x1080',
      scale_reference='Chalkboard grid of unknown cell size', scale_status='UNVERIFIED', timebase_status='CREATOR_LABEL_200FPS_20X_SLOWMO_AND_BURNT_IN_TIMER_UNVERIFIED',
      suitability='Real thrown paper bag (strong air drag), static camera, release visible; burnt-in creator strobe dots/timer/text overlays; not vacuum free fall', capture_group='RHETOS_MATHE_AC_BALLISTIC'),
 dict(clip_id='N1', experiment='swing_drop_impact', title="ORION 10' Swing Drop (Documentation)", source_url='https://images.nasa.gov/details/ORION10ftSwingDrop_Documentation', original_source_url='https://images.nasa.gov/details/ORION10ftSwingDrop_Documentation',
      download_url='https://images-assets.nasa.gov/video/ORION10ftSwingDrop_Documentation/ORION10ftSwingDrop_Documentation~medium.mp4', creator="NASA Langley Research Center / photographer Gary Banziger", licence='PD-USGov-NASA', licence_url='https://www.nasa.gov/nasa-brand-center/images-and-media/',
      attribution="NASA Langley Research Center / photographer Gary Banziger - ORION 10' Swing Drop (Documentation); NASA Image and Video Library; no endorsement implied", file='shards/NASA/N1.mp4', source_duration_label='see ffprobe', source_resolution='source 1920x1080; local ~medium 1280x720',
      scale_reference='Test-rig/backdrop size undocumented here', scale_status='UNVERIFIED', timebase_status='EDITED_DOCUMENTARY_TIMEBASE_UNVERIFIED',
      suitability="Cable swing then release ~0.5 s before splash; low contrast; people walk through frame; NOT counted", capture_group='NASA_LARC_LANDIR_N1'),
 dict(clip_id='N2', experiment='swing_drop_impact', title="NASA Drop Test Supports Safer Air Taxi Designs", source_url='https://images.nasa.gov/details/LRC-2025-V-06242025-RVLT-Gantry-Drop-Test-With-Slate-V0002050', original_source_url='https://images.nasa.gov/details/LRC-2025-V-06242025-RVLT-Gantry-Drop-Test-With-Slate-V0002050',
      download_url='https://images-assets.nasa.gov/video/LRC-2025-V-06242025-RVLT-Gantry-Drop-Test-With-Slate-V0002050/LRC-2025-V-06242025-RVLT-Gantry-Drop-Test-With-Slate-V0002050~medium.mp4', creator="NASA LaRC OCIO Video Services (Bono Herrera)", licence='PD-USGov-NASA', licence_url='https://www.nasa.gov/nasa-brand-center/images-and-media/',
      attribution="NASA LaRC OCIO Video Services (Bono Herrera) - NASA Drop Test Supports Safer Air Taxi Designs; NASA Image and Video Library; no endorsement implied", file='shards/NASA/N2.mp4', source_duration_label='see ffprobe', source_resolution='source 3840x2160; local ~medium 1280x720',
      scale_reference='Test-rig/backdrop size undocumented here', scale_status='UNVERIFIED', timebase_status='EDITED_DOCUMENTARY_TIMEBASE_UNVERIFIED',
      suitability="Fuselage enters from off-frame, ~0.8 s visible fall, deformation/tumble; NOT counted", capture_group='NASA_LARC_LANDIR_N2'),
 dict(clip_id='N3', experiment='swing_drop_impact', title="Lift & Cruise Drop Test Documentary", source_url='https://images.nasa.gov/details/2022-H1_V_Lift&CruiseDropTest-5', original_source_url='https://images.nasa.gov/details/2022-H1_V_Lift&CruiseDropTest-5',
      download_url='https://images-assets.nasa.gov/video/2022-H1_V_Lift%26CruiseDropTest-5/2022-H1_V_Lift%26CruiseDropTest-5~medium.mp4', creator="NASA Langley Research Center / photographer Gary Banziger", licence='PD-USGov-NASA', licence_url='https://www.nasa.gov/nasa-brand-center/images-and-media/',
      attribution="NASA Langley Research Center / photographer Gary Banziger - Lift & Cruise Drop Test Documentary; NASA Image and Video Library; no endorsement implied", file='shards/NASA/N3.mp4', source_duration_label='see ffprobe', source_resolution='source 1920x1080; local ~medium 1280x720',
      scale_reference='Test-rig/backdrop size undocumented here', scale_status='UNVERIFIED', timebase_status='EDITED_DOCUMENTARY_TIMEBASE_UNVERIFIED',
      suitability="Cable-constrained swing tracked ~1.8 s; release unidentified; foreground tripod occludes final descent/impact; NOT counted", capture_group='NASA_LARC_LANDIR_N3'),
]
FLAGS = {'PD04': 'local 2D bob template tracking on all 600 decoded frames, not calibrated pendulum physics or distribution',
         'PD06': 'local 2D bob template tracking on all 280 decoded frames, not calibrated pendulum physics or distribution',
         'PD03': 'local moving-ball blob centroid on all 1793 decoded frames, 48 inspected crops; not calibrated physics or distribution',
         'RM05': 'local LK flow 60-90 s every decoded frame at 10-frame baseline: fundamental matrix explains, single homography does not (camera translation/parallax evidence); not reconstruction, scale or distribution',
         'RM02': 'local LK flow all 426 frames at 10-frame baseline: H inlier median 0.45 vs F 0.86 (parallax-consistent); not reconstruction, scale or distribution',
         'PJ03': 'real Earth thrown-bag projectile with air drag: local 2D template track, 20 fps resample of file 15-36 s, bag in box frames 0-320 of 420 (release, apex, early descent; 48 crops inspected); final descent/landing lost to burnt-in overlay dots; not vacuum g, scale or distribution',
         'ST03': 'real Earth apple drop: STOCK-shard HSV/diff track f58-76 (release to pillow contact) matches every inspected full-rate frame; 25p-in-30p repeats confirmed by integrator pixel diff; playback-time image-space only, capture slow-motion factor and scale unknown, never calibrated g or distribution',
         'BN01': 'real Earth small-ball floor bounces: file 13.0-15.6 s, all 624 full-rate frames template-tracked at 640 px; floor contacts with shadow meeting at seg f271/f433 viewed frame by frame; post-contact arcs f282-340 and f438-536 parabola RMS 0.5/0.4 px; image-space only, oblique perspective, scale unknown, 240 fps capture claimed not independently verified; not calibrated g, restitution or distribution'}
with MAN.open(encoding='utf-8', newline='') as f:
    rd = csv.DictReader(f); fields, rows = rd.fieldnames, list(rd)
have = {r['clip_id'] for r in rows}
for r in rows: r.update(UPD.get(r['clip_id'], {}))
for n in NEW:
    if n['clip_id'] in have: continue
    row = dict.fromkeys(fields, ''); fn = n.pop('file'); row.update(n)
    row.update(adaptation_notes='Identify edits; respect licence/attribution and depicted-person and publicity limits', status='UNAPPROVED_CANDIDATE', owner_approved='NO', local_path='test-data/public/' + fn, evidence_path=EVS.get(row['clip_id'], EV))
    rows.append(row)
rec = json.loads(REC.read_text(encoding='utf-8')); files = {x['clip_id']: x for x in rec['files']}
for row in rows:
    if not row['local_path'] or row['clip_id'] in files and row['clip_id'] not in FLAGS: continue
    p = ROOT / row['local_path']
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size:stream=codec_type,codec_name,avg_frame_rate,width,height', '-of', 'json', str(p)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video'); row['file_fps'] = v['avg_frame_rate']; row['file_duration_s'] = probe['format']['duration']
    item = files.get(row['clip_id']) or dict(clip_id=row['clip_id'], local_path=row['local_path'], source_url=row['source_url'], download_url=row['download_url'], licence=row['licence'], sha256=hashlib.sha256(p.read_bytes()).hexdigest(), probe=probe)
    if row['clip_id'] in FLAGS:
        item.update(usability_verified=True, usability_evidence=EVS.get(row['clip_id'], EV), usability_scope=FLAGS[row['clip_id']])
    files[row['clip_id']] = item
rec['files'] = [files[r['clip_id']] for r in rows if r['local_path']]
with MAN.open('w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, lineterminator='\n'); w.writeheader(); w.writerows(rows)
REC.write_text(json.dumps(rec, indent=2) + '\n', encoding='utf-8')
print('recorded', len(rec['files']), 'local files; verified', sum(1 for x in rec['files'] if x.get('usability_verified')))
