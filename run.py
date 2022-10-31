import sys
import os
import logging
#from pathlib import PosixPath
import flywheel
import json
import glob
import shutil

print(sys.path)

# logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('asltlbx-gear')
logger.info("=======: ASL gear :=======")

with flywheel.GearContext() as context:
    # Setup basic logging
    context.init_logging()
    config = context.config
    analysis_id = context.destination['id']
    gear_output_dir = context.output_dir
    run_script = os.path.join(gear_output_dir, "asl_run.sh")
    # output_root = gear_output_dir / analysis_id
    # working_dir = PosixPath(str(output_root.resolve()) + "_work")

    # Get relevant container objects
    fw = flywheel.Client(context.get_input('api_key')['key'])
    analysis_container = fw.get(analysis_id)
    project_container = fw.get(analysis_container.parents['project'])
    session_container = fw.get(analysis_container.parent['id'])
    subject_container = fw.get(session_container.parents['subject'])

    # Get subject and session names
    session_label = session_container.label
    subject_label = subject_container.label
    prefix = "sub-{}_ses-{}".format(subject_label, session_label)

    subjects = [subject_container.label]
    sessions = [session_container.label]

    project_label = project_container.label

    # Inputs
    asl_image_path = context.get_input_path('asl')
    m0_image_path = context.get_input_path('m0')
    aslcontext_path = context.get_input_path('aslcontext')
    fs_license_path = context.get_input_path('freesurfer_license')

    shutil.copy(fs_license_path, "/opt/freesurfer/.license")

    # Configs
    pld = config.get('PLD')
    ld = config.get('LD')
    m0scale = config.get('m0scale')
    m0type = config.get('m0type')
    fwhm = config.get('fwhm')
    labelefficiency = config.get('labelefficiency')
    asl_fwhm = config.get('asl_fwhm')
    dir = config.get('dir')
    # frac = float(config.get('bet_frac'))
    # alt_skullstrip = config.get('alt_skullstrip')


def write_command():
    """Write out command script."""
    with flywheel.GearContext() as context:
        cmd = ["/usr/local/miniconda/bin/python",
            "/opt/base/batch_run.py",
            "--aslfile {}".format(asl_image_path),
            "--m0file {}".format(m0_image_path),
            "--pld {}".format(pld),
            "--ld {}".format(ld),
            "--m0scale {}".format(m0scale),
            "--m0type {}".format(m0type),
            "--fwhm {}".format(fwhm),
            "--labelefficiency {}".format(labelefficiency),
            "--asl_fwhm {}".format(asl_fwhm),
            "--dir {}".format(dir),
            # "--frac {}".format(frac),
            # "--alt_skullstrip {}".format(alt_skullstrip),
            "--aslcontext '{}'".format(aslcontext_path),
            "--prefix {}".format(prefix),
            "--outputdir {}".format(gear_output_dir)
               ]

    logger.info(' '.join(cmd))
    # write command joined by spaces
    with open(run_script, 'w') as f:
        f.write(' '.join(cmd))

    return os.path.exists(run_script)


def main():
    os.system("bash -x /flywheel/v0/docker-env.sh")

    command_ok = write_command()
    if not command_ok:
        logger.warning("Critical error while trying to write run command.")
        return 1

    # run command
    os.system("chmod +x {0}".format(run_script))
    os.system(run_script)

    # transfer output files to gear output directory
    #os.system("cp -r /opt/base/output/* {}".format(gear_output_dir))
    os.system("rm -rf /flywheel/v0/output/asl_reference_wf")

    return 0


if __name__ == '__main__':
    sys.exit(main())
