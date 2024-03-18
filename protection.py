import ruamel.yaml
import argparse
import tensorflow as tf
from src import parameterProtection as prtct
import urllib.request
import os

def load_model(float_model_path):
    if not os.path.isfile(float_model_path):
        urllib.request.urlretrieve('https://gitlab.com/EHU-GDED/FLOSS/HSI-Drive/-/raw/wip/jon/ci/pycode/testing/pretrained_models/v2.0/example.h5?inline=false', './models/model.h5')
        trained_model = tf.keras.models.load_model('./models/model.h5', compile=False)
    else:
        trained_model = tf.keras.models.load_model(float_model_path, compile=False)
    return trained_model

def protection(float_model_path, confFile, protection_level, infoArray, verbose):

    yaml = ruamel.yaml.YAML()
    with open(confFile, 'r') as fp:
        data = yaml.load(fp)
    fp.close()

    # PROTECCIÓN
    with open(confFile, 'w') as fp:
        data['Action'] = 'protection'
        data['Upp_thr'] = None
        data['Low_thr'] = None
        yaml.dump(data, fp)
    fp.close()

    trained_model = load_model(float_model_path)
    prtct.actions(model=trained_model, confFile=confFile, infoArray = infoArray, verbose=verbose)
    trained_model.save(float_model_path[:-3] + "_u" + str(protection_level) + "_l" + str(protection_level) + ".h5")

def main():

    ap = argparse.ArgumentParser()
    ap.add_argument('-m', '--model_path',         type=str, default="./models/example.h5", help="Path where the model is stored")
    ap.add_argument('-c', '--conf_file',          type=str, default="./conf/completivenessAnalysis.yaml", help="Path where completivenessAnalysis.yaml is stored.")
    ap.add_argument('-p', '--protection_level',   type=int, default=0, help="The protection level that is going to be applied.")
    ap.add_argument('-i', '--info_array',         type=str, default="./conf/completiveness_analysis_u0_l0.npy", help="Path where the analysis .npy file is stored.")
    ap.add_argument('-v', '--verbose',            type=int, default=0, help="Verboisity level with between 0 and 2.")

    args = ap.parse_args()

    protection(args.model_path, args.conf_file, args.protection_level, args.info_array, args.verbose)

if __name__ ==  "__main__":
    main()