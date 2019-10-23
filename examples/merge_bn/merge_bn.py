import numpy as np  
import sys,os  
caffe_root = '../../'
sys.path.insert(0, caffe_root + 'python')  
import caffe  

#train_proto = 'mobilenet_yolov3_test.prototxt'  
#train_model = 'mobilenet_yolov3_deploy_iter_55000.caffemodel'  #should be your snapshot caffemodel

#deploy_proto = 'remove_bn.prototxt'  
#save_model = 'remove_bn.caffemodel'

def merge_bn(net, nob):
    '''
    merge the batchnorm, scale layer weights to the conv layer, to  improve the performance
    var = var + scaleFacotr
    rstd = 1. / sqrt(var + eps)
    w = w * rstd * scale
    b = (b - mean) * rstd * scale + shift
    '''
    for key in net.params.iterkeys():
        if type(net.params[key]) is caffe._caffe.BlobVec:
            if key.endswith("/bn") or key.endswith("/scale") or 'batch_norm' in key or 'bn_scale' in key:
		continue
            else:
                conv = net.params[key]
                print(key)
                if not net.params.has_key(key + "/bn") :
                    for i, w in enumerate(conv):
                        nob.params[key][i].data[...] = w.data
                else:

                    bn = net.params[key + "/bn"]
                    scale = net.params[key + "/scale"]
                    #bn = net.params[key.replace('conv','batch_norm')]
                    #scale = net.params[key.replace('conv','bn_scale')]
                    #print(bn)
                    wt = conv[0].data
                    channels = wt.shape[0]
                    bias = np.zeros(wt.shape[0])
                    if len(conv) > 1:
                        bias = conv[1].data
                    mean = bn[0].data
                    var = bn[1].data
                    scalef = bn[2].data

                    scales = scale[0].data
                    shift = scale[1].data

                    if scalef != 0:
                        scalef = 1. / scalef
                    mean = mean * scalef
                    var = var * scalef
                    rstd = 1. / np.sqrt(var + 9.999999747378752e-06)
                    rstd1 = rstd.reshape((channels,1,1,1))
                    scales1 = scales.reshape((channels,1,1,1))
                    wt = wt * rstd1 * scales1
                    bias = (bias - mean) * rstd * scales + shift
                    
                    nob.params[key][0].data[...] = wt
                    nob.params[key][1].data[...] = bias
  

#net = caffe.Net(train_proto, train_model, caffe.TRAIN)  
#net_deploy = caffe.Net(deploy_proto, caffe.TEST)  

#merge_bn(net, net_deploy)
#net_deploy.save(save_model)
