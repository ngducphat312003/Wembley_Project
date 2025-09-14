import neoapi
import cv2
import sys
# camera = neoapi.Cam()
# camera.Connect()   
# camera.f.ExposureTime.Set(1000)
# camera.f.Width.Set(2592)
# camera.f.Height.Set(2048)

# camera.f.OffsetX.Set(0)
# camera.f.Gain.Set(0)
# camera.f.PixelFormat.Set(neoapi.PixelFormat_BayerRG8)
# camera.SetSynchronFeatureMode(False) 

# #Tắt sharpending
# camera.f.TriggerMode.value = neoapi.TriggerMode_On
# trigger = camera.f.TriggerSoftware
# if camera.HasFeature("SharpeningEnable"):
#     camera.SetFeature("SharpeningEnable", False)
# if camera.HasFeature("NoiseReductionEnable"):
#     camera.SetFeature("NoiseReductionEnable", False)

# #Bật chế độ use optimal buffer size
# if camera.HasFeature("UseOptimalBufferSize"):
#     camera.SetFeature("UseOptimalBufferSize", True)
# img_camera = camera.GetImage()
# cv2.namedWindow('finalImg', cv2.WINDOW_NORMAL)
# cv2.imshow("finalImg",img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

 
result = 0
try:
    camera = neoapi.Cam()
    camera.Connect()

    isColor = True
    if camera.f.PixelFormat.GetEnumValueList().IsReadable('BGR8'):
        camera.f.PixelFormat.SetString('BGR8')
    elif camera.f.PixelFormat.GetEnumValueList().IsReadable('Mono8'):
        camera.f.PixelFormat.SetString('Mono8')
        isColor = False
    else:
        print('no supported pixelformat')
        sys.exit(0)

    camera.f.ExposureTime.Set(10000)
    camera.f.AcquisitionFrameRateEnable.value = True
    camera.f.AcquisitionFrameRate.value = 10

    # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
    # Define the fps to be equal to 10. Also frame size is passed.
    #video = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc(*'MJPG'), 10,
                            # (camera.f.Width.Set(2592), camera.f.Height.Set(2048)), isColor)
    # video = cv2.VideoWriter('outpy.avi',cv2.VideoWriter_fourcc(*'DIVX'), 10,
    video = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc(*'XVID'), 10,
                            (camera.f.Width.value, camera.f.Height.value), isColor)

    for cnt in range(0, 200):
        img = camera.GetImage().GetNPArray()
        title = 'press ESC to exit ..'
        cv2.namedWindow(title, cv2.WINDOW_NORMAL)
        cv2.imshow(title, img)
        video.write(img)

        if cv2.waitKey(1) == 27:
            break

    cv2.destroyAllWindows()
    video.release()

except (neoapi.NeoException, Exception) as exc:
    print('error: ', exc)
    result = 1

sys.exit(result)