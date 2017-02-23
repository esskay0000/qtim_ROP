from os.path import isdir, isfile, join, basename, splitext, split
from common import find_images, imgs_to_unet_array
from PIL import Image
from mask_retina import create_mask
from keras.models import model_from_json

try:
    from retinaunet.lib.help_functions import *
    from retinaunet.lib.extract_patches import *
    from retinaunet.lib.pre_processing import my_PreProc
except ImportError:
    print "Unable to import retinaunet - is it on your path?"
    exit()


def segment_unet(input_path, out_dir, model):

    # Get list of images to segment
    im_list = []
    if isdir(input_path):
        im_list.extend(find_images(input_path))
    elif isfile(input_path):
        im_list.append(input_path)
    else:
        raise IOError("Please specify a valid image path or folder of images")

    # Pre-process the images, and return as patches
    img_patches, new_height, new_width, img_masks = preprocess_images(im_list, 48, 48, 5, 5)

    # Define model
    _, model_basename = split(model)
    model_arch = join(model, model_basename + '_architecture.json')
    model_weights = join(model, model_basename + '_best_weights.h5')

    model = model_from_json(open(model_arch).read())
    model.load_weights(model_weights)

    # Get predictions
    print "Running predictions..."
    predictions = model.predict(img_patches, batch_size=32, verbose=2)
    pred_imgs = pred_to_imgs(predictions)

    # Reconstruct images
    segmentations = recompone_overlap(pred_imgs, new_height, new_width, 5, 5)  # not sure about the stride widths

    for im_name, seg, mask in zip(im_list, segmentations, img_masks):

        # Mask the segmentation and transpose
        seg_masked = seg * mask
        seg_T = np.transpose(seg_masked, (1, 2, 0))

        # Save masked segmentation
        name, ext = splitext(basename(im_name))
        filename = join(out_dir, name + '_seg' + ext)
        print "Writing {}".format(filename)

        visualize(seg_T, filename)


def preprocess_images(img_list, patch_height, patch_width, stride_height, stride_width):

    imgs_original, masks = imgs_to_unet_array(img_list)
    test_imgs = my_PreProc(imgs_original)

    # Pad images so they can be divided exactly by the patches dimensions
    test_imgs = paint_border_overlap(test_imgs, patch_height, patch_width, stride_height, stride_width)
    test_masks = paint_border_overlap(masks, patch_height, patch_width, stride_height, stride_width)

    # Extract patches from the full images
    patches_imgs_test = extract_ordered_overlap(test_imgs, patch_height, patch_width, stride_height, stride_width)

    return patches_imgs_test, test_imgs.shape[2], test_imgs.shape[3], test_masks


if __name__ == "__main__":

    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-i', '--images', help="Image or folder of images", dest='images', required=True)
    parser.add_argument('-o', '--out-dir', help="Output directory", dest="out_dir", required=True)
    parser.add_argument('-u', '--unet', help='retina-unet dir', dest='model', required=True)
    args = parser.parse_args()

    segment_unet(args.images, args.out_dir, args.model)