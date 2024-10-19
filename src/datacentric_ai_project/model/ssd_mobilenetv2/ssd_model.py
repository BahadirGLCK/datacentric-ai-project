import torch
import torch.nn as nn
import torch.nn.functional as F
import math

class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels, kernel_size, stride, padding, groups=1, activation=True):
        super(ConvBlock, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size, stride, padding, groups=groups, bias=False)
        self.bn = nn.BatchNorm2d(out_channels)
        self.activation = activation

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        if self.activation:
            x = F.relu6(x)
        return x

class InvertedResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride, expansion_factor):
        super(InvertedResidualBlock, self).__init__()
        hidden_dim = in_channels * expansion_factor
        self.use_res_connect = self.stride == 1 and in_channels == out_channels

        layers = []
        if expansion_factor != 1:
            layers.append(ConvBlock(in_channels, hidden_dim, kernel_size=1, stride=1, padding=0))
        layers.extend([
            ConvBlock(hidden_dim, hidden_dim, kernel_size=3, stride=stride, padding=1, groups=hidden_dim),
            nn.Conv2d(hidden_dim, out_channels, kernel_size=1, stride=1, padding=0, bias=False),
            nn.BatchNorm2d(out_channels)
        ])
        self.block = nn.Sequential(*layers)

    def forward(self, x):
        if self.use_res_connect:
            return x + self.block(x)
        else:
            return self.block(x)

class MobileNetV2(nn.Module):
    def __init__(self, width_mult=1.0):
        super(MobileNetV2, self).__init__()
        self.cfgs = [
            [1, 16, 1, 1],
            [6, 24, 2, 2],
            [6, 32, 3, 2],
            [6, 64, 4, 2],
            [6, 96, 3, 1],
            [6, 160, 3, 2],
            [6, 320, 1, 1],
        ]
        input_channel = 32
        last_channel = 1280
        self.features = [ConvBlock(3, input_channel, kernel_size=3, stride=2, padding=1)]
        self.features.extend(self._make_layers(input_channel, width_mult))
        self.features.append(ConvBlock(input_channel, last_channel, kernel_size=1, stride=1, padding=0))
        self.features = nn.Sequential(*self.features)

    def _make_layers(self, in_channels, width_mult):
        layers = []
        for t, c, n, s in self.cfgs:
            out_channels = int(c * width_mult)
            for i in range(n):
                stride = s if i == 0 else 1
                layers.append(InvertedResidualBlock(in_channels, out_channels, stride, expansion_factor=t))
                in_channels = out_channels
        return layers

    def forward(self, x):
        return self.features(x)

class SSDHead(nn.Module):
    def __init__(self, num_classes, num_default_boxes=6):
        super(SSDHead, self).__init__()
        self.num_classes = num_classes
        self.loc_layers = nn.ModuleList([
            nn.Conv2d(96, num_default_boxes * 4, kernel_size=3, padding=1),
            nn.Conv2d(320, num_default_boxes * 4, kernel_size=3, padding=1),
        ])
        self.cls_layers = nn.ModuleList([
            nn.Conv2d(96, num_default_boxes * num_classes, kernel_size=3, padding=1),
            nn.Conv2d(320, num_default_boxes * num_classes, kernel_size=3, padding=1),
        ])

    def forward(self, xs):
        loc_preds = []
        cls_preds = []

        for i, x in enumerate(xs):
            loc_preds.append(self.loc_layers[i](x).permute(0, 2, 3, 1).contiguous())
            cls_preds.append(self.cls_layers[i](x).permute(0, 2, 3, 1).contiguous())

        loc_preds = torch.cat([o.view(o.size(0), -1) for o in loc_preds], 1)
        cls_preds = torch.cat([o.view(o.size(0), -1) for o in cls_preds], 1)

        loc_preds = loc_preds.view(loc_preds.size(0), -1, 4)
        cls_preds = cls_preds.view(cls_preds.size(0), -1, self.num_classes)

        return loc_preds, cls_preds

class SSDMobileNetV2(nn.Module):
    def __init__(self, num_classes=21, width_mult=1.0):
        super(SSDMobileNetV2, self).__init__()
        self.num_classes = num_classes
        self.backbone = MobileNetV2(width_mult=width_mult)
        self.ssd_head = SSDHead(num_classes=num_classes)

    def forward(self, x):
        features = []
        for i, layer in enumerate(self.backbone.features):
            x = layer(x)
            if i == 10 or i == 17:
                features.append(x)
        loc_preds, cls_preds = self.ssd_head(features)
        return loc_preds, cls_preds
    
class SSDAnchors:
    def __init__(self, feature_map_shapes, scales, aspect_ratios):
        self.feature_map_shapes = feature_map_shapes
        self.scales = scales
        self.aspect_ratios = aspect_ratios

    def generate_anchors(self):
        anchors = []
        for i, shape in enumerate(self.feature_map_shapes):
            fm_anchors = self._generate_anchors_for_feature_map(shape, self.scales[i], self.aspect_ratios[i])
            anchors.append(fm_anchors)
        anchors = torch.cat(anchors, dim=0)
        return anchors

    def _generate_anchors_for_feature_map(self, shape, scale, aspect_ratios):
        fm_anchors = []
        for i in range(shape):
            for j in range(shape):
                cx = (j + 0.5) / shape
                cy = (i + 0.5) / shape
                anchor = [cx, cy, scale, scale]
                fm_anchors.append(anchor)

                for ar in aspect_ratios:
                    if ar == 1:
                        continue
                    sqrt_ar = math.sqrt(ar)
                    fm_anchors.append([cx, cy, scale * sqrt_ar, scale / sqrt_ar])
                    fm_anchors.append([cx, cy, scale / sqrt_ar, scale * sqrt_ar])

        return torch.tensor(fm_anchors).view(-1, 4)

def nms(boxes, scores, iou_threshold=0.5, top_k=200):
    keep = []
    if boxes.numel() == 0:
        return torch.tensor(keep, dtype=torch.long)

    x_min = boxes[:, 0]
    y_min = boxes[:, 1]
    x_max = boxes[:, 2]
    y_max = boxes[:, 3]

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
    def __init__(self, num_classes=21, width_mult=1.0):
        super(SSDModelWithAnchorsAndNMS, self).__init__()
        self.ssd = SSDMobileNetV2(num_classes, width_mult=width_mult)
        self.anchors_generator = SSDAnchors(feature_map_shapes=[38, 19, 10, 5, 3, 1], 
                                            scales=[0.1, 0.2, 0.375, 0.55, 0.725, 0.9], 
                                            aspect_ratios=[[1, 2, 0.5]] * 6)
        
    def forward(self, x):
        loc_preds, cls_preds = self.ssd(x)  # SSD predictions
        anchors = self.anchors_generator.generate_anchors()  # Generate anchors
        
        batch_size = loc_preds.size(0)
        results = []
        
        for i in range(batch_size):
            boxes = loc_preds[i]  # Predictions for ith image in the batch
            scores, labels = cls_preds[i].max(dim=1)  # Get max class score and corresponding label
            keep = nms(boxes, scores)  # Apply NMS
            results.append((boxes[keep], labels[keep], scores[keep]))  # Keep NMS filtered results
        
        return results
