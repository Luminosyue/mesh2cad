"""Standalone mesh-derived CAD code, with embedded vertex and triangle data.

This reconstructs a faceted BREP, not an inferred sketch/extrusion feature tree.
Original numeric coordinates are retained; physical STL units are unknown.
Open meshes remain CAD surfaces. No guessed closures or thickness are added.
Run: python part_XXX_cad.py [--output-directory PATH] [--no-validate]
"""
from pathlib import Path
import argparse,base64,io,json,time,zlib
import numpy as np
import cadquery as cq
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing

PART_NAME = 'part_005'
SOURCE_INFO = {'source_path': '/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_stl/416ea8eb185542499bab9b523c072fd6/part_005.stl', 'relative_path': '416ea8eb185542499bab9b523c072fd6/part_005.stl', 'source_sha256': '0a82ad8fe354fc5357928eff90a61bbda00ab03b767045af8ebaf608c4ce2354', 'input_faces': 312, 'input_vertices': 210, 'input_watertight': False, 'input_winding_consistent': True, 'input_bounds': [[-0.2255132794380188, -0.2732551693916321, -0.2707625925540924], [0.22722779214382172, 0.42829254269599915, 0.33977600932121277]]}
GEOMETRY_BASE85 = 'c$}r033N@@8pn@lj3r27rq|R+-H;ec4aqgD7!svsu5!)9JVqV!^wdm=;Yx}aVu+!JNRP;XB!<>hEp81@2W@HlX!~CDo$vepmutIkt+(FGTHpHr&ObZ*?EUS1_BneK6`B9F08M_XXm<xa-WY0LQoODOXp<b{CJY<s7+-tzn5p@+6718DTUT}J)-kGQK5ddVJ!p_){J?QRjV(b<2R90`T7m}0jGHiS!07%l;|4j%Z!=)zc!%kaA39)+!@RCpH!Rd@sTXXu%&`2AKSj(Y=$mimd`4~gGV)-ADfUj~b4m3-&xjv1X+K@t{Kp(;|JuE5_M^)rbNS@Iw$ZgKCW(Fh;WaL=T|U2()bhi2DIa{8eOKU$IR3jmi^Z>(#=cQ?*%7|aeO>$xRgZGHvaL?jwPjOx@oyD6#Qvj<T)MU=)fIotM+exCxXSIfS^dR-(2jj0FFu{Fjg!U1U%GJ*`OfgsySaWxVewnF-p&4=L-FjN`t6+b_nTc@Z|x7)alb}h6aVsjuE%yY<5SL0-X->RV+FU<Ik(1ME;lt>{AVs{XUxj8oVPxoh~MWN=hrwjm;2>hKTG_F;m0^{tuJtS%k1x1wR;l}^Zg38=l1B$cCfGK|CaNnPcC|%^HZv$lwUT3ePiw@u1~*MJ(Kg%+@8+;33)Py>%Ux-ecflL<Uel(kE0g)G=u9&-E)TPIrav(Q+sxveSJ-1u2<_Y>l3c`L9X~S=4SByYD_)B^{rheer$Fo*R%NVJYJTBCF1vWh~I0P!TIU+f!w!NQO=Kca~0=V%k9Lzt=|WyIL|)aW^;f0y({JO3L9MRPgfR~8_`VsKBdyQ9nRA`_<n`0QjcFR_O*_Ad>^}`jFhh)f12~(wdE<ko}Vl8Xy$$PwPy3r^Z1WH$i8+pl>2K`50U(*?GpdqGw#17If3W1v7w>V<G)(^+ri1@^@;h}*F)#=xER5^rJi$P{CBoW$y~o}NecVg>_Xz7?kn}&FMEO8AC!^CzmN5kc0T!)+i7W;$NeyT`*Ggvi*Bvw--rB5{JxS;OP^cv+{OMX{Z8sB<-gYxxIMkLiyydxeOvp-GXD?wi(lw~wDV3Fw@3TAz^6Q(zdih%{c&^Icg5B^!tH;M$k(=$iSzjSZuVh*4!-DdiOXHBEaNdHiG52)AFfBs47tedjf-dB)i{^0^`$*H-?n#FNcpStxxA%BAlG9YS}guw%fI0Hv+n5yzJ5Fe<=63j^()cb9%D`s_H7Za9Iki%)j0NDn+|b1clF@<^{2rXxgD3I**C8A;Q4Lb+pw40JG`FwQ%A`<m9vANGiS}~2l>8%hxoo)xe#u@t4(M2?Kd6lTOKdq{@J%CBy)Ry@#VZZ8#R}CGcT5X`{3`nysg$rZjbZnQ1&hHp_0$Uev+puR`#7O?{WK`ap7FvGWs9;SwDQAeS4uZ;?D`#%Ht3^-NE%l2TK0keu>&cxSpeHc%88M`-$KFFMhvhuAoaV`8lg)oebW2j_c|Ahm-vqfAD+7=#Z54lE36T@h^wSysB|a{ALr*ay|KK@pxJeUl-pxnCrEj+QjqUc_o*9{l^3z2Uq0+SugoBHp_Un94F69%?0cm6|Gmfzjsrwc>1=LrLS@QaW|x2M`y`>EuCfkx)z)1>D$sfvagTLk@sxHBJA6Te|3iMvm`Ln)7OjN5dU~HE^klxX*1W8f5s)QKRzwPo3F>E@I1Aj$z8?mse5ZXk6(>#S>Ajty1L}EeLVYmM%+tzun%9i%3Izn^A|4XzwdsI-<QU+9Iw89p|jLqvy1q17xQ!P?Efg!s~^yv?`t^TUcmmCQZf#y53;=Z&Lg9^ej_=ZpI5!kcf8)%O1Lt;`Icg>xPJZoH)FY;)XN*$FaCShOMZ&@#(<g9{u@t6ay?Ua9Oe6ddo9zOZ!Bso^<TGk<$8ye<oRQ)cp&fj#3fzWuetOFmwOg2&wcvJPMqJKDLk)?hU?`$@mleAJWrb4<@sm$HD1E)vlp(z<u}#mdYsm-JpP*Fz*{oj!@lD2tJYThgdT5ld0X<AJTJ3H%Y83?o)=EOE95%2Xa6rUuhJ`ovmU-D?f>UI&ZDb&R15ZN4&`=gZP)TTqK%Dh#qDU}&-EBLoAZ3PITPFP^V27leW$Cb^y^}3Tb?f?{pC3d*v#vm^LE21Z@zXrEy`Ox&L`KSz1>#}`nikOc7`wS>aAbKzqa&_@Ro-@clt$m$(zx8RR0Jsc{YwUw?}vx7fTJlK@ncYQE#_j)>CEN?Ng$8Jyqw4twhzK5nkq%D|_L@2ru(f_1*K+p7hg{2ru*hxv$KBd)3HA5ni4z)ptK%+Le^WtjhDN`tIjfvj@uern)|;KGp{<HBx+K{V{r;7Jqe7{$6pG=_vKb_gcg4RMs(LmP34X-P2aE|H}HQ`0n-7__2qR$46P8Ro}fn>qmcJ|CRM0zPkQfx(?jR_f_66ZeM-BXz4@QSKnW5Uwwbs$L`zeEkDnF<^8BdAD8wh@89RX^8PhHsKi&^@7kjq;w$fW+rCHQtKSc9U-^E}-gqLu@_q8$SH4fQYzObh)bAYIhZ}i+t9}<byMD?3E8kIf9?E`L`R>x6`E$F~?=)w^XR_Z`zUwSm3EUs``%vqbF23?T>2yuweW3bXs$HqX`)Tz%S?e&Fzth$4aLpCT-|^~qyRq<=`0985u3EBRQuYOU@A~Yk`v~XQ2I4FG4x?M1)T8WEocnEjt?p}#--n5>?1NkhO?bbg?wf39W8_-dXK9b`u&?gR?1y~ic~$mz&h-=7SND(F(plmw`%U|z4dN^NRwMm_?1z>8uWl_U&%Lsb)_q!uuk6PS+dO{W)P22c#BKJ~a{yz16?s0Ca|7+nG4|DS2IrEm#aGTH>^t&jv#*?ESgb|FSI#}08~oUR<(%YatN6;fioUA3_{uqq?O|*2m2(?cuSoHga~|#M;o>XjLPqv7@s)EV!~dB0%DIzqBTaneoXRM7TYTkQOW%B7@}Qi9xqK_-NPm@cvzqy2omS4-TseW_d!EZhy>!~BHz?t2@iS9zMqw>L8$7_{sF6(iajW;E#$omUtE0wxVRirCqsAz+4ewF+%^>cA>xE{_HDe1@2b0>t9nDx{#=Fq<VA4(CcfqX@#4Vv)z*|sfOK2Z3X%BEqa2se>a2s%YXm@aXa3^RlFlj$9=?CC0=>JCu;^he9mC#P$PWaoE&=0|+v%#eE!K919E5U1_e*>=tZ-6cYFGP-rdz#VLj26%V;MHbyFymurJ1}W0@W<ed&=%m0;LXqhVA5G&(s^LgMc~cgIOtMv9C#gc37B*NcpZ2ZbPkwwCU}_{D>Rvt?}4MCtH9CV&d`})(t%*o{$SGH;LhMk==)&OZs168TWC*kPvncZxEXYA{|18CN27mk(6sz!6opq5eo^?u`OKi@qZrf|{5teCs4v)R##?5TMi5s-5Qmu282S$ME$}<whEOZG8MGGE3a$*T4z+@-gUdoogUf=8B1)qluY-$0D}sxG3n7Sup&{U4aBYvi)kYB0Iy@OV1KJqe7=50BAf5(o2zK{>8iIH_f_Nx`*oGi(jvx+))&hrvYaob&JaQU@Abt};>~BUvs2{X4xH9tYhafJDAT9ze3ofg@n0GX9N_mV0aem~V@}3W>f$49Gqi)gyVA7Hv_butso|0%gX$f#mGn$%F*9?albud<S;7x`$1y2S?Aev&Fo1!lFxDyAXz0~fi&|q*d%2Y)VmxtB`4>KdiV|<CHqn*@_5zran5#X^1;*rp4;E~`_(COe&;L*?+a6#nCA3^*k+D2_^0JVV|fEz)ZgGs}|q&2{ez-17`)u2J(Al$PWv;?@m8DVC;ZAKGlJp^$mGz=UHu7Ieby;u*4izA2&Ac)=br6lfK5`HyA6|}ty>Ma8e^XOL?`Wl9IyZc@rIU5Fzfz}7dfJY<hW31|<Z|<>s8)NIvg?p@t-SdH%=7<AY2igSO1i7n&Ag+rbra4K^9{spKC#!<#`K9&06f{74@eGstAkU<gpryc-z!qo#H~{rq5X9x6<-z6AwsO!=a5-=wv;w#S+7Sq?1g?a85T7>VQ!}!l7r<HIOz3%VCOE^4i)N&oaT1yXrr+hlO9#{MPMDEo#$hv#Lia+Gz@I=9p-EuUec(j!4l}kx_dxf7_kfQfh*O|R;3Tvu1#!Zok0+3W6KJ11C&XtE#AzP=AwCC9g&qZ`f)65ylc9UT$>2i>;slSpBp`^L2;!{>;;9JY!3g3Z&_r+|@-+lOJjf%b#KWQS(Cy%O@NVcH@NV#a=rQnq@L2?LIy6OlF;9pypqbi>c|`gd^gNi#U-YPx_!7p5#^yAFI2%E1K-0kPF*6Xvr_9)9#sM>SB8ZP8h>zfYM?Bha1bsb%GVZ<~KyD78UU#mxdE|2&^1TiBBaVgcg6;&9KMCG&@F3_IFzH0_An*|A1ntGR6Ay-t2T##t4vm8j21iBa^9jiRpZ+V)iyxgAPS5|?qyFW~+j7sp9BmeQzDbXY^riQbxq$lcqJEa%K-#|n|7!ZK'

def decode_geometry():
    with np.load(io.BytesIO(zlib.decompress(base64.b85decode(GEOMETRY_BASE85)))) as data:
        return data['vertices'],data['faces']

def build():
    vertices,faces=decode_geometry()
    center=(vertices.min(axis=0)+vertices.max(axis=0))/2
    extent=float(np.ptp(vertices,axis=0).max())
    if extent<=0: raise ValueError('Source has zero extent')
    construction_scale=100.0/extent
    v=(vertices-center)*construction_scale
    sewing=BRepBuilderAPI_Sewing(1e-7,True,True,True,False)
    planar_faces=[]
    skipped=[]
    for index,tri in enumerate(faces):
        points=v[tri]
        if np.linalg.norm(np.cross(points[1]-points[0],points[2]-points[0]))<=1e-12:
            skipped.append(index)
            continue
        wire=cq.Wire.makePolygon([cq.Vector(*p) for p in points],close=True)
        face=cq.Face.makeFromWires(wire)
        planar_faces.append(face)
        sewing.Add(face.wrapped)
    if not planar_faces: raise ValueError('No non-degenerate triangles')
    sewing.Perform()
    shape=cq.Shape.cast(sewing.SewedShape())
    representation='faceted_surface'
    if SOURCE_INFO['input_watertight']:
        solids=[]
        for shell in shape.Shells():
            solid=cq.Solid.makeSolid(shell)
            if solid.Volume()<0: solid=cq.Shape.cast(solid.wrapped.Reversed())
            solids.append(solid)
        if solids:
            candidate=solids[0] if len(solids)==1 else cq.Compound.makeCompound(solids)
            if candidate.isValid() and len(candidate.Faces())==len(planar_faces):
                shape=candidate
                representation='faceted_solid'
    if not shape.isValid():
        # Explicitly represent troublesome nonmanifold edges as separate faces.
        shape=cq.Compound.makeCompound(planar_faces)
        representation='independent_faces'
    shape=shape.scale(1/construction_scale).translate(tuple(center))
    return shape,{'representation':representation,'degenerate_faces_skipped':skipped,
                  'construction_scale':construction_scale,
                  'sewing_tolerance_original_units':1e-7/construction_scale}

def describe(shape):
    b=shape.BoundingBox()
    return {'valid':bool(shape.isValid()),'solids':len(shape.Solids()),
            'shells':len(shape.Shells()),'faces':len(shape.Faces()),
            'bounds':[[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]],
            'solid_volume':float(shape.Volume()) if shape.Solids() else None}

def export(out,validate=True):
    start=time.time();out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shape,metadata=build()
    state=describe(shape)
    if not state['valid']: raise RuntimeError('Constructed BREP is invalid')
    shape.exportBrep(str(out/(PART_NAME+'.brep')))
    shape.exportStep(str(out/(PART_NAME+'.step')))
    report={**SOURCE_INFO,**metadata,'cad':state,'step_unit':'mm',
            'source_physical_unit':'unknown','coordinate_policy':'preserve original numeric coordinates',
            'code_kind':'standalone embedded faceted geometry','source_modified':False}
    if validate:
        reopened=cq.importers.importStep(str(out/(PART_NAME+'.step'))).val()
        report['step_reimport']=describe(reopened)
        if not report['step_reimport']['valid']: raise RuntimeError('Reimported STEP is invalid')
        if report['step_reimport']['faces']!=state['faces']:
            raise RuntimeError('STEP transfer changed the face count')
        error=float(np.max(np.abs(np.asarray(report['step_reimport']['bounds'])-np.asarray(state['bounds']))))
        report['roundtrip_bounds_max_error']=error
        if error>max(float(np.ptp(decode_geometry()[0],axis=0).max())*1e-5,1e-6):
            raise RuntimeError('STEP transfer changed bounding dimensions')
    report['seconds']=time.time()-start
    report['status']='SUCCESS'
    (out/(PART_NAME+'_report.json')).write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-directory',type=Path,default=Path(__file__).resolve().parent)
    parser.add_argument('--no-validate',action='store_true')
    args=parser.parse_args()
    print(json.dumps(export(args.output_directory,not args.no_validate)),flush=True)
