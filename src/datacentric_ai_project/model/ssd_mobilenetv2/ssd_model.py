import torch
import torch.nn as nn
import torch.nn.functional as F
from torchinfo import summary
from collections import OrderedDict
import math
import torchvision
from torchvision.models import mobilenet_v2

# Depthwise Convolution Module
class DepthWise_Conv(nn.Module):
    def __init__(self, in_fts, stride=(1,1)) -> None:
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_fts, in_fts, kernel_size=(3,3), stride=stride, padding=(1,1), groups=in_fts, bias=False),
            nn.BatchNorm2d(in_fts),
            nn.ReLU6(inplace=True)
        )

    def forward(self, input_image):
        x = self.conv(input_image)
        return x


# PointWise Convolution Module
class Pointwise_Conv(nn.Module):
    def __init__(self, in_fts, out_fts) -> None:
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_fts, out_fts, kernel_size=(1,1), bias=False),
            nn.BatchNorm2d(out_fts)
        )
    def forward(self, input_image):
        x = self.conv(input_image)
        return x

class NetForStrideOne(nn.Module):
    def __init__(self, in_fts, out_fts, expansion) -> None:
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_fts, expansion*in_fts, kernel_size=(1,1), bias=False),
            nn.BatchNorm2d(expansion*in_fts),
            nn.ReLU6(inplace=True)
        )
        self.dw = DepthWise_Conv(expansion*in_fts)
        self.pw = Pointwise_Conv(expansion*in_fts, out_fts)

        self.in_fts = in_fts
        self.out_fts = out_fts
        self.expansion = expansion

    def forward(self, input_image):
        if self.expansion == 1:
            x = self.dw(input_image)
            x = self.pw(x)
        else:
            x = self.conv1(input_image)
            x = self.dw(x)
            x = self.pw(x)

        # If input channel and output channel are same, then perform add
        # residual part
        if self.in_fts == self.out_fts:
            x = input_image + x          

        return x

class NetForStrideTwo(nn.Module):
    def __init__(self, in_fts, out_fts, expansion) -> None:
        super().__init__()
        self.conv1 = nn.Sequential(
            nn.Conv2d(in_fts, expansion*in_fts, kernel_size=(1,1), bias=False),
            nn.BatchNorm2d(expansion*in_fts),
            nn.ReLU6(inplace=True)
        )
        self.dw = DepthWise_Conv(expansion*in_fts, stride=(2,2))
        self.pw = Pointwise_Conv(expansion*in_fts, out_fts)

        self.expansion = expansion

    def forward(self, input_image):
        if self.expansion == 1:
            x = self.dw(input_image)
            x = self.pw(x)
        else:
            x = self.conv1(input_image)
            x = self.dw(x)
            x = self.pw(x)      

        return x

# MobileNetV2 architecture
class MobileNetV2New(nn.Module):
    def __init__(self, bottleneckLayerDetails, in_fts=3, numClasses=3, width_multiplier=1) -> None:
        super().__init__()
        self.bottleneckLayerDetails = bottleneckLayerDetails
        self.width_multiplier = width_multiplier

        self.conv1 = nn.Sequential(
            nn.Conv2d(in_fts, round(width_multiplier*32), kernel_size=(3,3), stride=(2,2), padding=(1,1), bias=False),
            nn.BatchNorm2d(round(width_multiplier*32)),
            nn.ReLU6(inplace=True)
        )
        self.in_fts = round(width_multiplier*32)
        
        # Defined bottleneck layer as per Table 2
        self.layerConstructed = self.constructLayer()

        # Top layers after bottleneck
        self.feature = nn.Sequential(
            nn.Conv2d(self.in_fts, round(width_multiplier*1280), kernel_size=(1,1), bias=False),
            nn.BatchNorm2d(round(width_multiplier*1280)),
            nn.ReLU6(inplace=True)
        )

        self.avgpool = nn.AdaptiveAvgPool2d(output_size=(1,1))

        self.outputLayer = nn.Sequential(
            nn.Dropout2d(),
            nn.Conv2d(round(width_multiplier*1280), numClasses, kernel_size=(1,1)),
        )

    def forward(self, input_image):
        x = self.conv1(input_image)
        x = self.layerConstructed(x)
        x = self.feature(x)
        x = self.avgpool(x)
        x = self.outputLayer(x)
        return x

    # Defined function to construct the layer based on bottleneck layer defined in Table 2
    def constructLayer(self):
        itemIndex = 0
        block = OrderedDict()
        # iterating the defined layer details
        for lItem in self.bottleneckLayerDetails:
            # each items assigned corresponding values
            t, out_fts, n, stride = lItem
            # If width multipler is mentioned then perform this line
            out_fts = round(self.width_multiplier*out_fts)
            # for stride value 1
            if stride == 1:
                # constructedd the NetForStrideOne module by n times
                for nItem in range(n):
                    block[str(itemIndex)+"_"+str(nItem)] = NetForStrideOne(self.in_fts, out_fts, t)
                    self.in_fts = out_fts
            # for stride value 2
            elif stride == 2:
                # First layer constructed for NetForStrideTwo module once only
                block[str(itemIndex)+"_"+str(0)] = NetForStrideTwo(self.in_fts, out_fts, t)
                self.in_fts = out_fts
                # Remaining will be NetForStrideOne module (n-1) times
                for nItem in range(1,n):
                    block[str(itemIndex)+"_"+str(nItem)] = NetForStrideOne(self.in_fts, out_fts, t)
            itemIndex += 1

        return nn.Sequential(block)


class MobileNetV2Backbone(nn.Module):
    def __init__(self, pretrained=True, feature_layer_indices=None):
        super(MobileNetV2Backbone, self).__init__()
        # Load pretrained MobileNetV2
        model = mobilenet_v2(pretrained=pretrained)
        self.feature_layer_indices = feature_layer_indices or [6, 13]  #TODO: Example indices

        # Extract features up to the last convolutional block
        self.features = model.features  # Sequential container of features

    def forward(self, x):
        features = []
        for i, layer in enumerate(self.features):
            x = layer(x)
            if i in self.feature_layer_indices:
                features.append(x)
        return features
    

# SSDHead Class
class SSDHead(nn.Module):
    """
    SSD Head for object detection with classification and localization layers.
    """
    def __init__(self, feature_channels, num_classes, num_default_boxes=6):
        super(SSDHead, self).__init__()
        self.num_classes = num_classes
        self.num_default_boxes = num_default_boxes

        self.loc_layers = nn.ModuleList([
            nn.Conv2d(channels, num_default_boxes * 4, kernel_size=3, padding=1)
            for channels in feature_channels
        ])
        self.cls_layers = nn.ModuleList([
            nn.Conv2d(channels, num_default_boxes * num_classes, kernel_size=3, padding=1)
            for channels in feature_channels
        ])

    def forward(self, features):
        loc_preds, cls_preds = [], []
        for i, feature in enumerate(features):
            # Debugging shapes
            print(f"Feature {i} shape: {feature.shape}, Expected channels: {self.loc_layers[i].in_channels}")

            # Generate location and class predictions
            loc_out = self.loc_layers[i](feature)
            cls_out = self.cls_layers[i](feature)

            # Permute and flatten to match anchor format
            loc_preds.append(loc_out.permute(0, 2, 3, 1).contiguous())
            cls_preds.append(cls_out.permute(0, 2, 3, 1).contiguous())

        # Concatenate predictions across feature maps
        loc_preds = torch.cat([p.view(p.size(0), -1) for p in loc_preds], dim=1)
        cls_preds = torch.cat([p.view(p.size(0), -1) for p in cls_preds], dim=1)

        # Reshape predictions to match anchors
        loc_preds = loc_preds.view(loc_preds.size(0), -1, 4)
        cls_preds = cls_preds.view(cls_preds.size(0), -1, self.num_classes)

        return loc_preds, cls_preds


# SSDMobileNetV2 Class
class SSDMobileNetV2(nn.Module):
    """
    SSD Model with MobileNetV2 as the backbone.
    """
    #def __init__(self, bottleneckLayerDetails, num_classes=21, width_multiplier=1.0, num_default_boxes=6, feature_layer_indices = [5, 10, 14, 16, 18, 19]):
    def __init__(self, num_classes=21, feature_layer_indices=[1, 3, 5, 8, 12, 18], num_default_boxes=6):
        super(SSDMobileNetV2, self).__init__()
        #self.backbone = MobileNetV2(bottleneckLayerDetails, width_multiplier=width_multiplier)
        #self.backbone = mobilenet_v2(weights=torchvision.models.MobileNet_V2_Weights)
        self.backbone = MobileNetV2Backbone(pretrained=True, feature_layer_indices=feature_layer_indices)

        # Feature map extraction layers from the backbone
        self.feature_layer_indices = feature_layer_indices  # Adjust these based on MobileNetV2 architecture
        #self.feature_channels = [round(width_multiplier * 64), round(width_multiplier * 320)]
        #feature_channels = [self.backbone.features[idx][-1].out_channels for idx in feature_layer_indices]
        feature_channels = self._get_feature_channels(torch.randn(1,3,300,300)) #TODO: Make it more robust

        self.ssd_head = SSDHead(feature_channels, num_classes, num_default_boxes)

    #def forward(self, x):
    #    features = []
    #    x = self.backbone.conv1(x)
    #    for i, layer in enumerate(self.backbone.layerConstructed):
    #        x = layer(x)
    #        if i+4 in self.feature_layer_indices: #We already passed some layers in conv1
    #            features.append(x)

        # Pass the extracted feature maps through SSD head
    #    loc_preds, cls_preds = self.ssd_head(features)
    #    return loc_preds, cls_preds

    def forward(self, x, return_features=False):
        """
        Forward pass for SSD with MobileNetV2 backbone.
        """
        features = []
        for idx, layer in enumerate(self.backbone.features):
            x = layer(x)
            if idx in self.feature_layer_indices:
                features.append(x)  # Collect feature maps at specified indices

        loc_preds, cls_preds = self.ssd_head(features)
        if return_features:
            return loc_preds, cls_preds, features
        return loc_preds, cls_preds

    def _get_feature_channels(self, x):
        """
        Pass a dummy input through the backbone to determine feature channels dynamically.
        """
        feature_channels = []
        for idx, layer in enumerate(self.backbone.features):
            x = layer(x)
            if idx in self.feature_layer_indices:
                feature_channels.append(x.shape[1])  # Append the number of output channels
        return feature_channels

    
class SSDAnchors:
    """
    Generate default anchor boxes for SSD.
    """
    def __init__(self, feature_map_shapes, scales, aspect_ratios):
        self.feature_map_shapes = feature_map_shapes
        self.scales = scales
        self.aspect_ratios = aspect_ratios

    def generate_anchors(self):
        anchors = []
        total_anchors = 0
        for i, shape in enumerate(self.feature_map_shapes):
            fm_anchors = self._generate_anchors_for_feature_map(
                shape, self.scales[i], self.aspect_ratios[i]
            )
            print(f"Feature map {i} generates {fm_anchors.size(0)} anchors")
            total_anchors += fm_anchors.size(0)
            anchors.append(fm_anchors)
        print(f"Total anchors generated: {total_anchors}")
        return torch.cat(anchors, dim=0)

    def _generate_anchors_for_feature_map(self, shape, scale, aspect_ratios):
        anchors = []
        num_default_boxes = len(aspect_ratios) + 1
        for i in range(shape):
            for j in range(shape):
                cx, cy = (j + 0.5) / shape, (i + 0.5) / shape
                anchors.append([cx, cy, scale, scale])
                for ar in aspect_ratios:
                    if ar == 1:
                        continue
                    sqrt_ar = math.sqrt(ar)
                    anchors.append([cx, cy, scale * sqrt_ar, scale / sqrt_ar])
                    anchors.append([cx, cy, scale / sqrt_ar, scale * sqrt_ar])
        anchors = torch.tensor(anchors).view(-1, 4)
        assert anchors.size(0) == shape * shape * num_default_boxes, (
            f"Anchor mismatch: {anchors.size(0)} != {shape * shape * num_default_boxes}"
        )
        return anchors

def nms(boxes, scores, iou_threshold=0.5, top_k=200):
    """
    Non-Maximum Suppression for bounding box predictions.
    """
    keep = []
    if boxes.numel() == 0:
        return torch.tensor(keep, dtype=torch.long)

    x_min, y_min, x_max, y_max = boxes[:, 0], boxes[:, 1], boxes[:, 2], boxes[:, 3]
    areas = (x_max - x_min) * (y_max - y_min)
    _, order = scores.sort(0, descending=True)

    while order.numel() > 0:
        if len(keep) >= top_k:
            break
        i = order[0].item()
        keep.append(i)

        if order.numel() == 1:
            break

        xx_min = torch.max(x_min[i], x_min[order[1:]])
        yy_min = torch.max(y_min[i], y_min[order[1:]])
        xx_max = torch.min(x_max[i], x_max[order[1:]])
        yy_max = torch.min(y_max[i], y_max[order[1:]])

        w = torch.clamp(xx_max - xx_min, min=0)
        h = torch.clamp(yy_max - yy_min, min=0)

        intersection = w * h
        union = areas[i] + areas[order[1:]] - intersection
        iou = intersection / union

        order = order[1:][iou <= iou_threshold]

    return torch.tensor(keep, dtype=torch.long)

class SSDModelWithAnchorsAndNMS(nn.Module):
    """
    SSD Model with MobileNetV2 backbone, SSDHead, Anchors, and NMS.
    """
    #def __init__(self, bottleneck_layer_details, num_classes=21, width_multiplier=1.0, feature_map_shapes=[38, 19, 10, 5, 3, 1], 
    #             scales=[0.1, 0.2, 0.375, 0.55, 0.725, 0.9], aspect_ratios=[[1, 2, 0.5]] * 6, iou_threshold=0.5, top_k=200):
    #    super(SSDModelWithAnchorsAndNMS, self).__init__()
        #self.ssd = SSDMobileNetV2(
        #    bottleneck_layer_details, 
        #    num_classes=num_classes, 
        #    width_multiplier=width_multiplier
        #)
    def __init__(self, num_classes=21, scales=[0.1, 0.2, 0.375, 0.55, 0.725, 0.9],
                 aspect_ratios=[[1, 2, 0.5, 3]] * 6, iou_threshold=0.5, top_k=200):
        super(SSDModelWithAnchorsAndNMS, self).__init__()
        self.ssd = SSDMobileNetV2(num_classes, feature_layer_indices=[1, 3, 5, 8, 12, 18])

        _, _, feature_maps = self.ssd(torch.rand(1,3,300,300), return_features=True) #TODO:Make it more robust
        self.feature_map_shapes = [f.shape[2] for f in feature_maps]

        self.anchors_generator = SSDAnchors(
            feature_map_shapes=self.feature_map_shapes, 
            scales=scales, 
            aspect_ratios=aspect_ratios
        )
        self.iou_threshold = iou_threshold
        self.top_k = top_k

    def forward(self, x):
        # Get predictions and feature maps from SSD
        loc_preds, cls_preds = self.ssd(x)

        # Generate anchors
        anchors = self.anchors_generator.generate_anchors()

        # Ensure predictions and anchors are aligned
        assert loc_preds.size(1) == anchors.size(0), (
            f"Mismatch: loc_preds.size(1)={loc_preds.size(1)} anchors.size(0)={anchors.size(0)}"
        )

        batch_size = loc_preds.size(0)
        results = []

        for i in range(batch_size):
            # Decode bounding boxes
            boxes = self.decode_boxes(loc_preds[i], anchors)

            # Convert scores to probabilities and get labels
            scores, labels = cls_preds[i].softmax(dim=-1).max(dim=-1)

            # Apply NMS to remove overlapping boxes
            keep = nms(boxes, scores, self.iou_threshold, self.top_k)

            # Append results for the batch
            results.append({
                "boxes": boxes[keep],
                "labels": labels[keep],
                "scores": scores[keep]
            })

        return results

    def decode_boxes(self, loc_preds, anchors):
        """
        Decode bounding box predictions relative to anchor boxes.
        Handles mismatch in the number of predictions and anchors.
        """
        # Ensure loc_preds and anchors are matched
        num_anchors = anchors.size(0)
        loc_preds = loc_preds[:num_anchors, :]  # Trim predictions to match anchors

        # Initialize boxes tensor
        boxes = torch.zeros_like(loc_preds)  # Shape: [num_anchors, 4]

        # Extract anchor widths/heights and center coordinates
        anchors_wh = anchors[:, 2:]  # Width and height
        anchors_xy = anchors[:, :2]  # Center x and y

        # Decode center coordinates
        boxes[:, :2] = loc_preds[:, :2] * anchors_wh + anchors_xy

        # Decode width and height
        boxes[:, 2:] = torch.exp(loc_preds[:, 2:]) * anchors_wh

        # Convert to corner coordinates (top-left and bottom-right)
        boxes[:, :2] -= boxes[:, 2:] / 2  # Top-left corner
        boxes[:, 2:] += boxes[:, :2]      # Bottom-right corner

        return boxes


if __name__ == "__main__":
    # Bottleneck configurations for MobileNetV2

    #bottleneckLayerDetails = [
        # (expansion_factor, output_channels, num_blocks, stride)
    #    (1, 16, 1, 1),  # First bottleneck block
    #    (6, 24, 2, 2),  # Second bottleneck block
    #    (6, 32, 3, 2),  # Third bottleneck block
    #    (6, 64, 4, 2),  # Fourth bottleneck block
    #    (6, 96, 3, 1),  # Fifth bottleneck block
    #    (6, 160, 3, 2), # Sixth bottleneck block
    #    (6, 320, 1, 1), # Seventh bottleneck block
    #]

    # Initialize SSDMobileNetV2 with chosen feature layers
    #model = SSDMobileNetV2(
    #    bottleneckLayerDetails,
    #    num_classes=21,
    #    width_multiplier=1.0,
    #    num_default_boxes=6,
    #    feature_layer_indices=[10, 20]  # Adjusted based on MobileNetV2 configuration
    #)

    # Create dummy input for testing
    #dummy_input = torch.randn(1, 3, 300, 300)

    #model = SSDModelWithAnchorsAndNMS(num_classes=21)
    #results = model(dummy_input)
    #print(f"Decoded Boxes: {results[0]['boxes'].shape}")
    #print(f"Scores: {results[0]['scores'].shape}")
    #print(f"Labels: {results[0]['labels'].shape}")
    #m = MobileNetV2New(bottleneckLayerDetails, width_multiplier=1)
    #m = mobilenet_v2(progress=True)
    #summary(m, (1,3,300,300))

    # Perform a forward pass
    #loc_preds, cls_preds = model(dummy_input)

    # Verify output shapes
    #print(f"Location predictions shape: {loc_preds.shape}")  # Expected: [batch_size, num_predictions, 4]
    #print(f"Classification predictions shape: {cls_preds.shape}")  # Expected: [batch_size, num_predictions, num_classes]

    #all_model = SSDModelWithAnchorsAndNMS(
    #    bottleneckLayerDetails,
    #    num_classes=3,
    #    width_multiplier=1.0
    #)
    #results = all_model(dummy_input)
    #print(results)
    #print("All tests passed!")
    # ----------------------------
    #feature_layer_indices = [1, 3, 5, 8, 12, 18]
    #backbone = MobileNetV2Backbone(pretrained=True, feature_layer_indices=feature_layer_indices)
    #dummy_input = torch.randn(1, 3, 300, 300)  # Typical SSD input size
    #features = backbone(dummy_input)
    #for i, f in enumerate(features):
    #    print(f"Feature Map {i}: {f.shape}")
    feature_layer_indices = [1, 3, 5, 8, 12, 18]  # Adjust based on your selected feature maps
    
    # Load the SSD model with the MobileNetV2 backbone
    model = SSDModelWithAnchorsAndNMS(
        num_classes=21
    )

    # Create dummy input for testing
    dummy_input = torch.randn(1, 3, 300, 300)

    # Pass the input through the model
    results = model(dummy_input)

    # Print results
    for i, result in enumerate(results):
        print(f"Results for image {i}:")
        print(f"Boxes shape: {result['boxes'].shape}")
        print(f"Labels shape: {result['labels'].shape}")
        print(f"Scores shape: {result['scores'].shape}")