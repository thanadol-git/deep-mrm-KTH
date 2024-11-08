import torch

from torchvision import transforms as T
from torch.optim.lr_scheduler import StepLR

from mstorch.data.manager import DataManager
from mstorch.tasks import ObjectDetectionTask
from mstorch.utils.logger import get_logger
from mstorch.enums import PartitionType

from deepmrm import model_dir
from deepmrm.data.dataset import DeepMrmDataset
from deepmrm.data_prep import get_metadata_df
from deepmrm.model.boundary_detect import BoundaryDetector
from deepmrm.transform.make_input import MakeTagets, MakeInput
from deepmrm.train.trainer import BaseTrainer
from deepmrm.transform.augment import (
    RandomResizedCrop, 
    MultiplicativeJitter,
)
from deepmrm.data import obj_detection_collate_fn

logger = get_logger('DeepMRM')
num_workers = 4
gpu_index = 0
RANDOM_SEED = 2022
task = ObjectDetectionTask('peak_detect', box_dim=1, num_classes=2)

# Define transforms
transform = T.Compose([
                MakeInput(force_resampling=True, use_rt=False),
                MakeTagets()])

aug_transform = T.Compose([
        MakeInput(
            force_resampling=True, 
            use_rt=False),
        MultiplicativeJitter(
            p=0.25, 
            noise_scale_ub=1e-3, 
            noise_scale_lb=1e-4),
        RandomResizedCrop(p=0.7),
        MakeTagets()
    ])



def run_train(
    model_name, 
    #augmentation, 
    aug_transform=None,
    returned_layers=[3, 4], 
    batch_size = 512, 
    num_epochs = 100,
    split_ratio=(.8, .1, .1),
    use_scl=False,
    backbone='resnet18',
    only_peak_boundary=True,
    num_anchors=1):

    logger.info(f'Start loading dataset')
    label_df, pdac_xic, scl_xic = get_metadata_df(use_scl=use_scl, only_peak_boundary=only_peak_boundary)
    logger.info(f'Complete loading dataset')
    logger.info(f'#samples: {label_df.shape[0]}, #boundaries: {label_df["manual_boundary"].sum()}')

    ds = DeepMrmDataset(
                label_df,
                pdac_xic,
                scl_xic,
                transform=transform)
    
    data_mgr = DataManager(
                task, 
                ds, 
                num_workers=num_workers, 
                collate_fn=obj_detection_collate_fn, 
                split_ratio=split_ratio,
                random_seed=RANDOM_SEED)

    data_mgr.split()

    if aug_transform is not None:
        data_mgr.set_transform(aug_transform, partition_type=PartitionType.TRAIN)

    trainer = BaseTrainer(data_mgr, 
                          model_dir, 
                          logger, 
                          run_copy_to_device=False, 
                          gpu_index=gpu_index)

    model = BoundaryDetector(
                model_name, task, num_anchors=num_anchors, 
                returned_layers=returned_layers,
                backbone=backbone)
    
    optimizer = torch.optim.Adam(model.parameters())
    scheduler = StepLR(optimizer, step_size=10, gamma=0.5)
    trainer = trainer.set_model(model).set_optimizer(optimizer).set_scheduler(scheduler)

    ## start training
    trainer.train(num_epochs=num_epochs, batch_size=batch_size)


if __name__ == "__main__":
    
    run_train(
        "DeepMRM_BD_NoAug",
        #aug_transform=aug_transform,
        aug_transform=None,
        backbone='resnet18', 
        batch_size = 512,
        num_epochs = 100,
        only_peak_boundary=False,
    )
    
